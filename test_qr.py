import cv2
from pyzbar import pyzbar
from database import create_connection
from datetime import datetime
import time


def mark_attendance_from_qr(registration_no):
    """
    Mark attendance in database from QR code scan
    """
    try:
        conn = create_connection()
        if not conn:
            print("❌ Database connection failed")
            return False

        cursor = conn.cursor()

        # Check if already marked today
        cursor.execute("""
                       SELECT *
                       FROM attendance
                       WHERE registration_no = %s AND date = CURDATE()
                       """, (registration_no,))

        exists = cursor.fetchone()

        if exists:
            print(f"⚠️  Attendance already marked for {registration_no} today")
            cursor.close()
            conn.close()
            return False

        # Mark attendance
        cursor.execute("""
                       INSERT INTO attendance (registration_no, date, time, status)
                       VALUES (%s, CURDATE(), CURTIME(), 'Present')
                       """, (registration_no,))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Attendance marked for: {registration_no}")
        return True

    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
        return False


def scan_qr():
    """
    Scan QR code using webcam with proper error handling
    """
    print("\n" + "=" * 50)
    print("🎥 QR CODE SCANNER")
    print("=" * 50)
    print("📸 Starting webcam...")

    # Try to open webcam
    cap = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("❌ ERROR: Could not open webcam")
        print("💡 Troubleshooting:")
        print("   - Check if camera is connected")
        print("   - Close other apps using camera")
        print("   - Try running as administrator")
        return

    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("✅ Webcam started successfully!")
    print("\n📋 Instructions:")
    print("   • Show QR code to camera")
    print("   • Press 'Q' to quit")
    print("   • Auto-closes in 60 seconds")
    print("-" * 50)

    start_time = time.time()
    timeout = 60  # 60 seconds timeout
    last_scan = ""

    try:
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                print("\n⏰ Scanner timeout (60 seconds)")
                break

            # Read frame from camera
            ret, frame = cap.read()

            # Check if frame was read successfully
            if not ret or frame is None:
                print("⚠️  Warning: Failed to grab frame, retrying...")
                time.sleep(0.1)
                continue

            # Detect and decode QR codes
            try:
                decoded_objects = pyzbar.decode(frame)

                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')

                    # Avoid duplicate scans
                    if qr_data != last_scan:
                        print(f"\n🔍 QR Detected: {qr_data}")

                        # Validate registration number format
                        if qr_data.startswith(('STU', 'FAC')):
                            if mark_attendance_from_qr(qr_data):
                                print("✨ Success!")
                            last_scan = qr_data
                        else:
                            print("❌ Invalid QR code format")

                    # Draw rectangle around QR code
                    points = obj.polygon
                    if len(points) == 4:
                        pts = [(point.x, point.y) for point in points]
                        cv2.polylines(frame, [np.array(pts, np.int32)], True, (0, 255, 0), 3)

                    # Display QR data on frame
                    cv2.putText(frame, qr_data, (obj.rect.left, obj.rect.top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            except Exception as decode_error:
                # If decode fails, just continue to next frame
                pass

            # Add instructions on frame
            cv2.putText(frame, "Press 'Q' to Quit", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            remaining = int(timeout - (time.time() - start_time))
            cv2.putText(frame, f"Time: {remaining}s", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Display the frame
            cv2.imshow('QR Code Scanner', frame)

            # Check for 'Q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n🛑 Scanner stopped by user")
                break

    except KeyboardInterrupt:
        print("\n🛑 Scanner interrupted by user")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Camera released")
        print("=" * 50 + "\n")


# Test function
if __name__ == "__main__":
    print("Testing QR Scanner...")
    scan_qr()