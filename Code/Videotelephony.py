import socket
import threading

import cv2
import numpy


class Videotelephony:
    def __init__(self, dst_ip: str, dst_port: int, camera_number: int):
        self.udp_socket_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set Dst IP and Port
        self.ip_and_port = (dst_ip, dst_port)
        # Get Src IP
        local_hostname = socket.gethostname()
        local_ip = socket.gethostbyname(local_hostname)
        self.udp_socket_receiver.bind((local_ip, dst_port))
        self.cap = cv2.VideoCapture(camera_number)
        # Controll the threading stop condition
        self.stop_condition = False

    def __get_cam_information(self):
        _, frame = self.cap.read()
        return frame

    def __video_serialization(self, frame, image_compression_ratio=60):
        """
        Translate frame to bytes

        Args:
            frame: Original frame
            image_compression_ratio (int): If set this value to high, then frame quality is better, but it will make the tranlate speed down.
        """
        ecnode_param = [cv2.IMWRITE_JPEG_QUALITY, image_compression_ratio]
        _, imgencode = cv2.imencode('.jpg', frame, ecnode_param)
        byte_data = imgencode.tobytes()
        return byte_data

    def local_video_information(self):
        """
        Send data via UDP socket and show the frame on local
        """
        while True:
            ori_frame = self.__get_cam_information()
            cv2.imshow('LOCAL', ori_frame)
            byte_data = self.__video_serialization(ori_frame)
            try:
                self.udp_socket_sender.sendto(byte_data, self.ip_and_port)
            except:
                pass
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_condition = True
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def __video_deserialization(self, bytes_data):
        """
        Translate frame to bytes
        """        
        bytes_data = numpy.frombuffer(bytes_data, numpy.uint8)
        remote_frame = cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)
        return remote_frame

    def receive_video_information(self):
        while True:
            payload, self.dst_ip = self.udp_socket_receiver.recvfrom(102400)
            remote_frame = self.__video_deserialization(payload)
            cv2.imshow('REMOTE', remote_frame)
            cv2.waitKey(5)
            if self.stop_condition == True:
                break

    def main(self):
        remote_video = threading.Thread(target=self.receive_video_information)
        remote_video.start()
        local_video = threading.Thread(target=self.local_video_information)
        local_video.start()


videotelephony = Videotelephony('192.168.209.47', 30000, 1)
videotelephony.main()
