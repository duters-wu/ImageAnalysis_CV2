import sys
import ast
import getopt
import types
import numpy as np
import json
import math


def Cir_Line(Cir1, Cir2):
    x0 = Cir1[0]
    y0 = Cir1[1]
    R0 = Cir1[2]
    if x0 - Cir2[0] == 0:
        x1 = x0
        y1 = y0 + R0
        x2 = x0
        y2 = y0 - R0
    elif y0 - Cir2[1] == 0:
        x1 = x0 + R0
        y1 = y0
        x2 = x0 - R0
        y2 = y0
    else:
        Derta_y = R0/math.sqrt(1 + ((x0 - Cir2[0])/(y0 - Cir2[1]))**2)
        Derta_x = Derta_y/(abs(y0 - Cir2[1])/abs(x0 - Cir2[0]))
        if (y0 - Cir2[1])/(x0 - Cir2[0]) > 0:
            x1 = x0 + Derta_x
            y1 = y0 + Derta_y
            x2 = x0 - Derta_x
            y2 = y0 - Derta_y
        else:
            x1 = x0 + Derta_x
            y1 = y0 - Derta_y
            x2 = x0 - Derta_x
            y2 = y0 + Derta_y
    return [(x1, y1), (x2, y2)]


def insec(p1, r1, p2, r2):
    x = p1[0]
    y = p1[1]
    R = r1
    a = p2[0]
    b = p2[1]
    S = r2
    d = math.sqrt((abs(a-x))**2 + (abs(b-y))**2)
    if d-(R+S) > 2 or (abs(R-S)) - d > 2:
        print("Two circles have no intersection")
        return
    elif d == 0 and R == S:
        print("Two circles have same center!")
        return
    else:
        A = (R**2 - S**2 + d**2) / (2 * d)
        h = math.sqrt(abs(R**2 - A**2))
        x2 = x + A * (a-x)/d
        y2 = y + A * (b-y)/d
        x3 = round(x2 - h * (b - y) / d, 2)
        y3 = round(y2 + h * (a - x) / d, 2)
        x4 = round(x2 + h * (b - y) / d, 2)
        y4 = round(y2 - h * (a - x) / d, 2)
        c1 = np.array([x3, y3])
        c2 = np.array([x4, y4])
        return c1, c2


def main(argv):
    arg_dict = {}
    switches = {'li': list, 'di': dict, 'tu': tuple}
    singles = ''.join([x[0]+':' for x in switches])
    long_form = [x+'=' for x in switches]
    d = {x[0]+':': '--'+x for x in switches}
    try:
        opts, args = getopt.getopt(argv, singles, long_form)
    except getopt.GetoptError:
        print("bad arg")
        sys.exit(2)

    for opt, arg in opts:
        if opt[1]+':' in d:
            o = d[opt[1]+':'][2:]
        elif opt in d.values():
            o = opt[2:]
        else:
            o = ''
        if o and arg:
            arg_dict[o] = ast.literal_eval(arg)

        if not o or not isinstance(arg_dict[o], switches[o]):
            print(opt, arg, " Error: bad arg")
            sys.exit(2)

    for e in arg_dict:
        start = arg_dict[e]

    # 根据参照圆半径从小到大排序
    start.sort(key=lambda item: item[2])

    # 两个信号时的算法
    if len(start) == 2:
        cir1 = start[0]
        cir2 = start[1]
        # 两圆相离或外切
        if (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 >= (cir1[2] + cir2[2])**2:
            P1 = np.array([cir1[0], cir1[1]])
            R1 = cir1[2]
            P2 = np.array([cir2[0], cir2[1]])
            R2 = math.sqrt((cir2[1] - cir1[1])**2 +
                           (cir2[0]-cir1[0])**2) - cir1[2]
            crossPoint = insec(P1, R1, P2, R2)
            crossPoint_Cir_Line = Cir_Line(cir1, cir2)
            print(json.dumps(
                {"Cir_Line": crossPoint_Cir_Line, "X": crossPoint[0][0], "Y": crossPoint[0][1], "status_2_Points": 'Dissociation or tangent'}))

        # 两圆相交
        if (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 < (cir1[2] + cir2[2])**2 and (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 > (cir1[2] - cir2[2])**2:
            P1 = np.array([cir1[0], cir1[1]])
            R1 = cir1[2]
            P2 = np.array([cir2[0], cir2[1]])
            R2 = math.sqrt((cir1[0] - cir2[0])**2 +
                           (cir1[1] - cir2[1])**2) - R1
            crossPoint = insec(P1, R1, P2, R2)
            crossPoint_Cir_Line = Cir_Line(cir1, cir2)
            # crossPoint_Cir_Line_Centre = [(crossPoint_Cir_Line[0][0] + crossPoint_Cir_Line[1][0])/2,
            #                              (crossPoint_Cir_Line[0][1] + crossPoint_Cir_Line[1][1])/2]
            print(json.dumps(
                {"Cir_Line": crossPoint_Cir_Line, "X": (crossPoint[0][0] + crossPoint[1][0])/2, "Y": (crossPoint[0][1] + crossPoint[1][1])/2, "status_2_Points": 'Crossing'}))

        # 两圆内含或内切
        if (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 <= (cir1[2] - cir2[2])**2:
            P1 = np.array([cir1[0], cir1[1]])
            R1 = cir1[2]
            P2 = np.array([cir2[0], cir2[1]])
            R2 = math.sqrt((cir2[1] - cir1[1])**2 +
                           (cir2[0]-cir1[0])**2) + cir1[2]
            crossPoint = insec(P1, R1, P2, R2)
            crossPoint_Cir_Line = Cir_Line(cir1, cir2)
            print(json.dumps(
                {"Cir_Line": crossPoint_Cir_Line, "X": crossPoint[0][0], "Y": crossPoint[0][1], "status_2_Points": 'To inline cut or contain'}))

    # 三个以上个信号时的算法
    if len(start) >= 3:
        start = start[0:3]
        cir1 = start[1]
        cir2 = start[2]
        cir0 = start[0]
        # 两参照圆相离或外切
        if (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 >= (cir1[2] + cir2[2])**2:
            P1 = np.array([cir1[0], cir1[1]])
            R1 = cir1[2]
            P2 = np.array([cir2[0], cir2[1]])
            R2 = math.sqrt((cir2[1] - cir1[1])**2 +
                           (cir2[0]-cir1[0])**2) - cir1[2]
            crossPoint = insec(P1, R1, P2, R2)
            P1_ = np.array([cir0[0], cir0[1]])
            R1_ = cir0[2]
            P2_ = np.array([crossPoint[0][0], crossPoint[0][1]])
            if math.sqrt((crossPoint[0][0] - cir0[0])**2 + (crossPoint[0][1] - cir0[1])**2) != cir0[2]:
                R2_ = abs(math.sqrt((cir0[0] - crossPoint[0][0]) **
                                    2 + (cir0[1] - crossPoint[0][1])**2) - cir0[2])
                crossPoint_ = insec(P1_, R1_, P2_, R2_)
                print(json.dumps(
                    {"X": crossPoint_[0][0], "Y": crossPoint_[0][1], "status_3_Points": 'Dissociation or tangent'}))
            else:
                print(json.dumps(
                    {"X": crossPoint[0][0], "Y": crossPoint[0][1], "status_3_Points": 'Dissociation or tangent'}))
        # 两参照圆相交
        if (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 < (cir1[2] + cir2[2])**2 and (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 > (cir1[2] - cir2[2])**2:
            P1 = np.array([cir1[0], cir1[1]])
            R1 = cir1[2]
            P2 = np.array([cir2[0], cir2[1]])
            R2 = cir2[2]
            crossPoint = insec(P1, R1, P2, R2)
            crossPoint_cen = [(crossPoint[0][0] + crossPoint[1][0])/2,
                              (crossPoint[0][1] + crossPoint[1][1])/2]
            P1_ = np.array([cir0[0], cir0[1]])
            R1_ = cir0[2]
            P2_ = np.array([crossPoint_cen[0], crossPoint_cen[1]])
            if math.sqrt((crossPoint_cen[0] - cir0[0])**2 + (crossPoint_cen[1] - cir0[1])**2) != cir0[2]:
                R2_ = abs(math.sqrt((cir0[0] - crossPoint_cen[0]) **
                                    2 + (cir0[1] - crossPoint_cen[1])**2) - cir0[2])
                crossPoint_ = insec(P1_, R1_, P2_, R2_)
                print(json.dumps(
                    {"X": crossPoint_[0][0], "Y": crossPoint_[0][1], "status_3_Points": 'Crosssing'}))
            else:
                print(json.dumps(
                    {"X": crossPoint[0][0], "Y": crossPoint[0][1], "status_3_Points": 'Crossing'}))
        # 两参照圆内切或内含
        if (cir1[0] - cir2[0])**2 + (cir1[1] - cir2[1])**2 <= (cir1[2] - cir2[2])**2:
            P1 = np.array([cir1[0], cir1[1]])
            R1 = cir1[2]
            P2 = np.array([cir2[0], cir2[1]])
            R2 = math.sqrt((cir2[1] - cir1[1])**2 +
                           (cir2[0] - cir1[0])**2) + cir1[2]
            crossPoint = insec(P1, R1, P2, R2)
            P1_ = np.array([cir0[0], cir0[1]])
            R1_ = cir0[2]
            P2_ = np.array([crossPoint[0][0], crossPoint[0][1]])

            if math.sqrt((crossPoint[0][0] - cir0[0])**2 + (crossPoint[0][1] - cir0[1])**2) != cir0[2]:
                R2_ = abs(math.sqrt((cir0[0] - crossPoint[0][0]) **
                                    2 + (cir0[1] - crossPoint[0][1])**2) - cir0[2])
                crossPoint_ = insec(P1_, R1_, P2_, R2_)
                print(json.dumps(
                    {"X": crossPoint_[0][0], "Y": crossPoint_[0][1], "status_3_Points": 'To inline cut or contain'}))
            else:
                print(json.dumps(
                    {"X": crossPoint[0][0], "Y": crossPoint[0][1], "status_3_Points": 'To inline cut or contain'}))


if __name__ == '__main__':
    main(sys.argv[1:])
