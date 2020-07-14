
# Coding: utf-8

import sys
import types
from cv2 import cv2
import numpy as np
import json
import time

# 获取传递的参数
# @param {string} argv[0]：图像处理脚本名称
# @param {string} argv[1]：待分析图片路径
argv = {
    'file_name': sys.argv[0],
    'image_url': sys.argv[1],
}


def read_config():
    """"读取配置"""
    with open("config.json") as json_file:
        config = json.load(json_file)
    return config


class ImageAnalysis:
    def image_points_find(self, image_main):
        # 将点位红色边框左上角像素点的坐标筛选出来加入点位列表@image_points
        image_points = [(0, 0)]
        for y in range(1, image_main.shape[0]):
            for x in range(1, image_main.shape[1]):
                if 170 <= image_main[y, x][2] <= 255 and image_main[y-1, x][2] == 0 and image_main[y, x-1][2] == 0 and 170 <= image_main[y+1, x][2] <= 255 and 170 <= image_main[y, x+1][2] <= 255 and image_main[y-1, x-1][2] == 0 and 170 <= image_main[y+1, x+1][2] <= 255 and image_main[y+6, x+6][2] == 0:
                    if abs(y - image_points[-1][0]) >= 3 or abs(x - image_points[-1][1]) >= 3:
                        image_points.append((y, x))
        del image_points[0]
        return image_points

    def image_points_filter(self, image_points, image_init, image_point_width):
        # 过滤点位列表异常数据
        image_points_new = list()
        for point in image_points:
            image_point = image_init[point[0]:point[0] +
                                     image_point_width, point[1]:point[1] + image_point_width]
            image_point_height, image_point_width = image_point.shape[0], image_point.shape[1]
            if not (image_point[1, int(image_point_width/2)][2] < 170 or image_point[image_point_height-1, int(image_point_width/2)][2] < 170):
                image_points_new.append(point)
        return image_points_new

    def image_points_analysis(self, image_points_new, image_init, image_point_width, border_width):
        # 点位健康分析
        image_points_final = list()
        image_points_normal = list()
        image_points_abnormal = list()
        for image_point in image_points_new:
            is_health = True
            image_point_final = image_init[image_point[0]:image_point[0] +
                                           image_point_width, image_point[1]:image_point[1] + image_point_width]
            image_points_temp = list()
            for point_px_y in range(border_width + 1, image_point_final.shape[0] - border_width + 1):
                for point_px_x in range(border_width + 1, image_point_final.shape[1] - border_width + 1):
                    if image_point_final[point_px_y, point_px_x][2] <= 50:
                        image_points_temp.append(image_point_final)
            if len(image_points_temp) >= (image_point_final.shape[0] - border_width*2)**2 * 0.8:
                image_points_abnormal.append([image_point[1], -image_point[0]])
                is_health = False
            else:
                image_points_normal.append([image_point[1], -image_point[0]])
                is_health = True
            image_points_final.append(
                json.dumps({"Y": image_point[0], "X": image_point[1], "is_healthy": is_health}))
        return {"image_points_final": image_points_final, "image_points_normal": image_points_normal, "image_points_abnormal": image_points_abnormal}


def main(image_analysis, image_url, border_width, border_color_range, point_width_range):
    time_start = time.time()
    # 边框红色的HSV范围，不同光照条件下不一样，可再配置文件中灵活调整
    lower_red = np.array(border_color_range['lower_red'])
    upper_red = np.array(border_color_range['upper_red'])

    # 1.读入待分析图片
    image_init = cv2.imread(image_url)

    # 2.从BGR转换到HSV
    image_hsv = cv2.cvtColor(image_init, cv2.COLOR_BGR2HSV)

    # 3.inRange()：介于lower/upper之间的像素点转为白色，其余为黑色
    image_mask = cv2.inRange(image_hsv, lower_red, upper_red)

    # 4.只保留原图中的红色部分
    image_main = cv2.bitwise_and(image_init, image_init, mask=image_mask)

    # 将点位红色边框左上角像素点的坐标筛选出来加入点位列表@img_points
    image_points = image_analysis.image_points_find(image_main)

    # 过滤点位列表异常数据
    image_points_new = image_analysis.image_points_filter(
        image_points, image_init, point_width_range['lower_width'])

    # 点位健康分析
    image_points_final = image_analysis.image_points_analysis(
        image_points_new, image_init, point_width_range['lower_width'], border_width)['image_points_final']
    image_points_normal = image_analysis.image_points_analysis(
        image_points_new, image_init, point_width_range['lower_width'], border_width)['image_points_normal']
    image_points_abnormal = image_analysis.image_points_analysis(
        image_points_new, image_init, point_width_range['lower_width'], border_width)['image_points_abnormal']

    # 分析结果输出
    image_size = json.dumps(
        {"height": image_init.shape[0], "width": image_init.shape[1]})
    print(json.dumps({"image_size": image_size, "points_information": image_points_final, "points_all": len(image_points_new),
                      "points_normal": len(image_points_normal),
                      "points_normal_xy": image_points_normal,
                      "points_abnormal": len(image_points_abnormal),
                      "points_abnormal_xy": image_points_abnormal,
                      "time_used": round(time.time() - time_start, 2)}))


if __name__ == '__main__':
    # 读取配置文件
    config = read_config()
    # 生成图像分析对象模块
    imageAnalysis = ImageAnalysis()

    main(imageAnalysis, argv['image_url'], config['border_width'],
         config['border_color_range'], config['point_width_range'])
