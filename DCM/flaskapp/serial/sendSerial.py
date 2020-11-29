import serial
import struct


def sendSerial(mode, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude, A_Pulse_Width, V_Pulse_Width, A_Sensitivity, V_Sensitivity, VRP, ARP, PVARP, Rate_Smoothing, Activity_Threshold, Reaction_Time, Response_Factor, Recovery_Time, Function_Call, port):
    # Function_Call = 0 BY DEFAULT
    st = struct.Struct('<BBBBBddBBddHHBBdBBBB')

    serial_com = st.pack(mode, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude, A_Pulse_Width, V_Pulse_Width, A_Sensitivity,
                         V_Sensitivity, VRP, ARP, PVARP, Rate_Smoothing, Activity_Threshold, Reaction_Time, Response_Factor, Recovery_Time, Function_Call)

    print(serial_com)
    print(len(serial_com))
    uC = serial.Serial(port, baudrate=115200)
    uC.write(serial_com)
    # unpacked = st.unpack(serial_com)
    # print(unpacked)
    ser.close()


# sendSerial(1, 100, 110, 0, 10, 5.0, 5.0, 10, 20, 0.0, 4.0, 200, 0, 0, 0, 1.0, 1, 0, 0, 0, 'COM7')
