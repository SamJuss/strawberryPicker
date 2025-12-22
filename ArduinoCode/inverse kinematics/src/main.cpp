#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  150
#define SERVOMAX  600

// Arm lengths in cm
#define L1 20.0
#define L2 13.2
#define L3 7.0
// L0 = 4.1 cm
// bottom offset = 4.9 cm

// Servos
#define SERVO_BASE 0
#define SERVO_SHOULDER 1
#define SERVO_ELBOW 2
#define SERVO_WRIST 3
#define SERVO_SCISSOR 4

// Safety limits
#define SHOULDER_MAX 160
#define SHOULDER_MIN 10
#define ELBOW_MAX 140
#define WRIST_MIN_WHEN_ELBOW_MAX 90

float currentAngles[5] = {90, 125, 110, 120, 180};
float targetAngles[5]  = {90, 125, 110, 120, 180};

int angleToPulse(float angle) {
  return map((int)angle, 0, 180, SERVOMIN, SERVOMAX);
}

// ======================================================
// SAFETY CHECK FUNCTION
// ======================================================
bool isSafeToMove(float shoulder, float elbow, float wrist) {
  // Check shoulder limits
  if (shoulder > SHOULDER_MAX) {
    Serial.print("UNSAFE: Shoulder angle ");
    Serial.print(shoulder);
    Serial.print(" exceeds maximum of ");
    Serial.println(SHOULDER_MAX);
    return false;
  }
  
  if (shoulder < SHOULDER_MIN) {
    Serial.print("UNSAFE: Shoulder angle ");
    Serial.print(shoulder);
    Serial.print(" is below minimum of ");
    Serial.println(SHOULDER_MIN);
    return false;
  }
  
  // Check elbow limits
  if (elbow > ELBOW_MAX) {
    Serial.print("UNSAFE: Elbow angle ");
    Serial.print(elbow);
    Serial.print(" exceeds maximum of ");
    Serial.println(ELBOW_MAX);
    return false;
  }
  
  // Check wrist limits when elbow is at max
  if (elbow >= ELBOW_MAX && wrist < WRIST_MIN_WHEN_ELBOW_MAX) {
    Serial.print("UNSAFE: Wrist angle ");
    Serial.print(wrist);
    Serial.print(" is below minimum of ");
    Serial.print(WRIST_MIN_WHEN_ELBOW_MAX);
    Serial.print(" when elbow is at ");
    Serial.println(elbow);
    return false;
  }
  
  return true;
}

// ======================================================
// FORWARD KINEMATICS (UNMODIFIED — MATCHES YOUR MODEL)
// ======================================================
void computeForwardKinematics(float theta0, float theta1, float theta2,
                              float &x, float &y, float &z)
{
  float t0 = theta0 * PI / 180.0;
  float t1 = theta1 * PI / 180.0;
  float t2 = (theta2 - theta1) * PI / 180.0;

  float base_offset = 1.4;
  float base_offset_x = base_offset * cos(t0);
  float base_offset_y = base_offset * sin(t0);

  float y_arm = L1 * cos(t1) + L2 * cos(t2) + L3;
  float z_arm = L1 * sin(t1) - L2 * sin(t2);

  x = y_arm * cos(t0) + base_offset_x;
  y = y_arm * sin(t0) + base_offset_y;
  z = z_arm + 7.5; // height offset from ground to shoulder
}

// ======================================================
// INVERSE KINEMATICS (MATCHES YOUR FK EXACTLY)
// ======================================================
bool computeInverseKinematics(float x, float y, float z,
                              float &theta0, float &theta1, float &theta2, float &theta3,
                              float &dbg_shoulderTrigDeg,
                              float &dbg_shoulderRightDeg,
                              float &dbg_elbowTrigDeg,
                              float &dbg_wristTrigDeg)
{
  //prep
  float arm_length = sqrt(x*x + y*y);
  float Z = z - 7.5; // height offset from ground to shoulder

  float L3_offset = arm_length - L3;

  float C = sqrt(L3_offset * L3_offset + Z*Z);
  if (C > L1 + L2 || C < fabs(L1 - L2))
    return false;

  float a = L1;
  float b = L2;

  //base
  theta0 = atan2(y, x) * 180.0 / PI;

  //elbow
  float elbowtrig = (a*a + b*b - C*C) / (2*a*b);
  elbowtrig = constrain(elbowtrig, -1, 1);
  float elbowtrig_angle = acos(elbowtrig);

  theta2 = elbowtrig_angle * 180.0 / PI;

  dbg_elbowTrigDeg = elbowtrig_angle * 180.0 / PI;

  //shoulder and prep
  float shouldertrig = (a*a + C*C - b*b) / (2*a*C);
  shouldertrig = constrain(shouldertrig, -1, 1);
  float shouldertrig_angle = acos(shouldertrig);

  if (L3_offset > 0){
  float shoulder_rightangle = atan(Z / L3_offset);

  float shoulder = shouldertrig_angle + shoulder_rightangle;

  theta1 = (shoulder * 180.0 / PI);
  dbg_shoulderTrigDeg  = shouldertrig_angle * 180.0 / PI;
  dbg_shoulderRightDeg = shoulder_rightangle * 180.0 / PI;
  }

  else if (L3_offset == 0){
  float shoulder = shouldertrig_angle + PI/2;

  theta1 = (shoulder * 180.0 / PI);
  dbg_shoulderTrigDeg  = shouldertrig_angle * 180.0 / PI;
  }

  else if (L3_offset < 0){
  float shoulder_rightangle = PI - atan(Z / L3_offset);

  float shoulder = shouldertrig_angle - shoulder_rightangle;

  theta1 = (shoulder * 180.0 / PI);
    
  dbg_shoulderTrigDeg  = shouldertrig_angle * 180.0 / PI;
  dbg_shoulderRightDeg = shoulder_rightangle * 180.0 / PI;
  }

  //wrist with prep
  float L1_Z = a * fabs(sin(theta1 * PI / 180.0));
  float Wrist_Y = L3 + b * cos((fabs(theta2 - ((theta2 - 90) * 2) - theta1)) * PI / 180.0);
  float Wrist_Z = b * sin((fabs(theta2 - ((theta2 - 90) * 2) - theta1)) * PI / 180.0);

  if (Wrist_Z == 0){ // traingle check on L2 and L3, if their is no triangle, their is nothing to calculate
  theta3 = 90;
  dbg_wristTrigDeg = theta3;
  return true;
  }

  float Wrist_ZY = sqrt(Wrist_Y*Wrist_Y + Wrist_Z*Wrist_Z);
  float wristtrig = (L3*L3 + b*b - Wrist_ZY * Wrist_ZY) / (2*L3*b);
  wristtrig = constrain(wristtrig, -1, 1);
  float wristtrig_angle = acos(wristtrig);

  if (L1_Z <= Z){
  theta3 = (wristtrig_angle - PI/2) * 180.0 / PI;
  }

  else if (L1_Z > Z){
  float theta3_before = (wristtrig_angle - PI/2) * 180.0 / PI;
  theta3 = theta3_before - ((theta3_before - 90) * 2);
  }

  dbg_wristTrigDeg = theta3;

  return true;
}

// ======================================================
// Smooth move
// ======================================================
void moveToTargetAngles(float step, int delayTime) {
  // float step = 0.125;
  // int delayTime = 0.25;

  float maxChange = 0;
  for (int i = 0; i < 5; i++) {
    float change = abs(targetAngles[i] - currentAngles[i]);
    if (change > maxChange) maxChange = change;
  }

  int steps = maxChange / step;
  if (steps < 1) steps = 1;

  for (int s = 0; s <= steps; s++) {
    for (int i = 0; i < 5; i++) {
      float pos = currentAngles[i] + (targetAngles[i] - currentAngles[i]) * s / steps;
      pwm.setPWM(i, 0, angleToPulse(pos));
    }
    delay(delayTime);
  }

  for (int i = 0; i < 5; i++)
    currentAngles[i] = targetAngles[i];
}

void moveScissorOnce(float angle) {
  targetAngles[SERVO_SCISSOR] = angle;
  moveToTargetAngles(4, 0.01);
  //moveToTargetAngles(step, delayTime);
  //delay time means time between movements
  //step means how smooth the movement is
}

void moveScissorSecond(float angle) {
  targetAngles[SERVO_SCISSOR] = angle;
  moveToTargetAngles(4, 0.01);
}

void moveToDefaultAngles() {
  targetAngles[SERVO_BASE]     = 90;
  targetAngles[SERVO_SHOULDER] = 125; //125
  targetAngles[SERVO_ELBOW]    = 110; //110
  targetAngles[SERVO_WRIST]    = 90;
  targetAngles[SERVO_SCISSOR]  = 180;
  moveToTargetAngles(0.125, 0.25);
}

void moveToNinetyDegrees() {
  targetAngles[SERVO_BASE]     = 90;
  targetAngles[SERVO_SHOULDER] = 95;
  targetAngles[SERVO_ELBOW]    = 80;
  targetAngles[SERVO_WRIST]    = 90;
  targetAngles[SERVO_SCISSOR]  = 180;
  moveToTargetAngles(0.125, 0.25);
}

void moveToExtendedPosition() {
  targetAngles[SERVO_BASE]     = 90;
  targetAngles[SERVO_SHOULDER] = 50;
  targetAngles[SERVO_ELBOW]    = 35;
  targetAngles[SERVO_WRIST]    = 90;
  targetAngles[SERVO_SCISSOR]  = 180;
  moveToTargetAngles(0.125, 0.25);
}

// ======================================================
// SETUP
// ======================================================
void setup() {
  Serial.begin(9600);
  Serial.println("Enter i x y z");
  Serial.println("Enter f t0 t1 t2");

  pwm.begin();
  pwm.setPWMFreq(50);
  delay(10);

  for (int i = 0; i < 5; i++)
    pwm.setPWM(i, 0, angleToPulse(currentAngles[i]));
}

// ======================================================
// LOOP: USER COMMANDS + FK/IK + ANGLE DISPLAY
// ======================================================
void loop() {
  if (!Serial.available()) return;

  String input = Serial.readStringUntil('\n');
  input.trim();

  // Check command mode: IK or FK
  if (input.startsWith("i")) {
    input = input.substring(2);
    input.trim();

    int s1 = input.indexOf(' ');
    int s2 = input.indexOf(' ', s1 + 1);
    if (s1 < 0 || s2 < 0) {
      Serial.println("Use: IK x y z");
      return;
    }

    float x = input.substring(0, s1).toFloat();
    float z = input.substring(s1 + 1, s2).toFloat();
    float y = input.substring(s2 + 1).toFloat();

    float t0, t1, t2, t3;
    float dbgTrig, dbgRight, dbgElbow, dbgWrist;
    if (!computeInverseKinematics(x, y, z, t0, t1, t2, t3, dbgTrig, dbgRight, dbgElbow, dbgWrist)) {
      Serial.println("IK unreachable.");
      return;
    }

    Serial.print("Shoulder trig angle (deg): ");
    Serial.println(dbgTrig);
    Serial.print("Shoulder right angle (deg): ");
    Serial.println(dbgRight);
    Serial.print("Elbow angle (deg): ");
    Serial.println(dbgElbow);
    Serial.print("Wrist angle (deg): ");
    Serial.println(dbgWrist);

    float proposed_shoulder = t1 + 5;
    float proposed_elbow = t2 - ((t2 - 90) * 2) - 10;
    float proposed_wrist = t3 - ((t3 - 90) * 2);

    // SAFETY CHECK BEFORE MOVING
    if (!isSafeToMove(proposed_shoulder, proposed_elbow, proposed_wrist)) {
      Serial.println("MOVEMENT BLOCKED - Unsafe angles detected!");
      Serial.println("Arm will not move.");
      return;
    }

    targetAngles[SERVO_BASE]     = t0;
    targetAngles[SERVO_SHOULDER] = proposed_shoulder;
    targetAngles[SERVO_ELBOW]    = proposed_elbow;
    targetAngles[SERVO_WRIST]    = proposed_wrist;

    // Move arm first
    moveToTargetAngles(0.125, 0.25);

    // delay(3000); 

    // // Then move scissor
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);
    // delay(500);
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);
    // delay(500);
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);
    // delay(500);
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);

    // delay(1000);
    // // sh 160 sh 10 el 140 
    // moveToDefaultAngles();

    // FK check of the IK actual angles 
    float base_math   = currentAngles[SERVO_BASE];
    float shoulder_math =(currentAngles[SERVO_SHOULDER] - 5);
    float elbow_math  = currentAngles[SERVO_ELBOW] + 10;
    float fkx, fky, fkz;
    computeForwardKinematics(base_math, shoulder_math, elbow_math, fkx, fky, fkz);

    Serial.println("=== IK RESULTS ===");
    Serial.print("IK Angles: ");
    Serial.print(t0); Serial.print(" ");
    Serial.print(t1); Serial.print(" ");
    Serial.println(t2);

    Serial.print("Actual Servo Angles: ");
    Serial.print(currentAngles[0]); Serial.print(" ");
    Serial.print(currentAngles[1]); Serial.print(" ");
    Serial.println(currentAngles[2]);

    Serial.print("FK of IK angles: ");
    Serial.print(fkx); Serial.print(" ");
    Serial.print(fky); Serial.print(" ");
    Serial.println(fkz);

    Serial.println("===================");
    Serial.println(" ");
  }

  else if (input.startsWith("f")) {
    input = input.substring(2);
    input.trim();

    int s1 = input.indexOf(' ');
    int s2 = input.indexOf(' ', s1 + 1);
    if (s1 < 0 || s2 < 0) {
      Serial.println("Use: F t0 t1 t2");
      return;
    }

    float t0 = input.substring(0, s1).toFloat();
    float t1 = input.substring(s1 + 1, s2).toFloat();
    float t2 = input.substring(s2 + 1).toFloat();

    float proposed_shoulder = t1 + 5;
    float proposed_elbow = t2 - 10;
    float proposed_wrist = 90;

    // SAFETY CHECK BEFORE MOVING
    if (!isSafeToMove(proposed_shoulder, proposed_elbow, proposed_wrist)) {
      Serial.println("MOVEMENT BLOCKED - Unsafe angles detected!");
      Serial.println("Arm will not move.");
      return;
    }

    // Direct servo movement with offsets
    targetAngles[SERVO_BASE]     = t0;
    targetAngles[SERVO_SHOULDER] = proposed_shoulder;
    targetAngles[SERVO_ELBOW]    = proposed_elbow;
    targetAngles[SERVO_WRIST]    = proposed_wrist;

    // Move arm first
    moveToTargetAngles(0.125, 0.25);

    // delay(3000);

    // // Then move scissor
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);
    // delay(500);
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);
    // delay(500);
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);
    // delay(500);
    // moveScissorOnce(80);
    // delay(500);
    // moveScissorSecond(120);

    // delay(1000);

    // moveToDefaultAngles();

    float fx, fy, fz;
    computeForwardKinematics(t0, t1, t2, fx, fy, fz);

    Serial.println("=== FK INPUT ===");
    Serial.print("FK Input Angles: ");
    Serial.print(t0); Serial.print(" ");
    Serial.print(t1); Serial.print(" ");
    Serial.println(t2);

    Serial.print("Actual Servo Angles: ");
    Serial.print(currentAngles[0]); Serial.print(" ");
    Serial.print(currentAngles[1]); Serial.print(" ");
    Serial.print(currentAngles[2]); Serial.print(" ");
    Serial.println(currentAngles[3]);

    Serial.print("FK Result XYZ: ");
    Serial.print(fx); Serial.print(" ");
    Serial.print(fy); Serial.print(" ");
    Serial.println(fz);
    Serial.println("=================");
    Serial.println(" ");
  }
  else if (input.startsWith("r")) {
  moveToDefaultAngles();
  float fx, fy, fz;
  computeForwardKinematics(currentAngles[SERVO_BASE], currentAngles[SERVO_SHOULDER], currentAngles[SERVO_ELBOW], fx, fy, fz);

  Serial.println("=== RESET ===");

  Serial.print("Actual Servo Angles: ");
  Serial.print(currentAngles[0]); Serial.print(" ");
  Serial.print(currentAngles[1]); Serial.print(" ");
  Serial.print(currentAngles[2]); Serial.print(" ");
  Serial.println(currentAngles[3]);

  Serial.print("Current XYZ: ");
  Serial.print(fx); Serial.print(" ");
  Serial.print(fy); Serial.print(" ");
  Serial.println(fz);
  Serial.println("=================");
  Serial.println(" ");
  }

  else if (input.startsWith("9")) {
  moveToNinetyDegrees();
  float fx, fy, fz;
  computeForwardKinematics(currentAngles[SERVO_BASE], currentAngles[SERVO_SHOULDER], currentAngles[SERVO_ELBOW], fx, fy, fz);

  Serial.println("=== NINETY ===");

  Serial.print("Actual Servo Angles: ");
  Serial.print(currentAngles[0]); Serial.print(" ");
  Serial.print(currentAngles[1]); Serial.print(" ");
  Serial.print(currentAngles[2]); Serial.print(" ");
  Serial.println(currentAngles[3]);

  Serial.print("Current XYZ: ");
  Serial.print(fx); Serial.print(" ");
  Serial.print(fy); Serial.print(" ");
  Serial.println(fz);
  Serial.println("=================");
  Serial.println(" ");
  }

  else if (input.startsWith("e")) {
  moveToExtendedPosition();
  float fx, fy, fz;
  computeForwardKinematics(currentAngles[SERVO_BASE], currentAngles[SERVO_SHOULDER], currentAngles[SERVO_ELBOW], fx, fy, fz);

  Serial.println("=== EXTEND ===");

  Serial.print("Actual Servo Angles: ");
  Serial.print(currentAngles[0]); Serial.print(" ");
  Serial.print(currentAngles[1]); Serial.print(" ");
  Serial.print(currentAngles[2]); Serial.print(" ");
  Serial.println(currentAngles[3]);

  Serial.print("Current XYZ: ");
  Serial.print(fx); Serial.print(" ");
  Serial.print(fy); Serial.print(" ");
  Serial.println(fz);
  Serial.println("=================");
  Serial.println(" ");
  }

  else if (input.startsWith("c")) {
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);
    delay(500);
    moveScissorOnce(80);
    delay(500);
    moveScissorSecond(120);

  Serial.println("=== CUT ===");
  }
}
