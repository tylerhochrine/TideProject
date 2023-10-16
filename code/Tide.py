#!/usr/bin/env python
from samplebase import SampleBase
import time
import multiprocessing as mp
import Functions as func
import Animation as anim


PIXEL_MULTI = 3.12727272
WATER_COLOR_R = 0
WATER_COLOR_G = 157
WATER_COLOR_B = 196


class Tide(SampleBase):
    data = {'dtmTime': '', 'tideHeight': 0, 'airTemp': 0}
    q = mp.Queue()

    def __init__(self, *args, **kwargs):
        super(Tide, self).__init__(*args, **kwargs)
        func.wait_for_internet_connection()

        self.data = func.get_data(self.data)

        self.q.put(self.data)


    def get_data(self, q):
        while True:
            self.data = func.get_data(self.data)
            self.q.put(self.data)

    
    def display_time(self, width, height, canvas, ltime):
        canvas.SetPixel(width-12, height-4, 0, 0, 0)
        canvas.SetPixel(width-12, height-6, 0, 0, 0)

        first_d = anim.CLOCK_NUMS[ltime[0]]
        second_d = anim.CLOCK_NUMS[ltime[1]]
        third_d = anim.CLOCK_NUMS[ltime[2]]
        fourth_d = anim.CLOCK_NUMS[ltime[3]]

        first_start_w, first_start_h = width - 21, height - 7
        second_start_w, second_start_h = width - 16, height - 7
        third_start_w, third_start_h = width - 10, height - 7
        fourth_start_w, fourth_start_h = width - 5, height - 7

        for x in range(3):
            for y in range(5):
                if ltime[0] != 0:
                    if first_d[y][x] == 1:
                        canvas.SetPixel(first_start_w + x, first_start_h + y, 0, 0, 0)
                if second_d[y][x] == 1:
                    canvas.SetPixel(second_start_w + x, second_start_h + y, 0, 0, 0)
                if third_d[y][x] == 1:
                    canvas.SetPixel(third_start_w + x, third_start_h + y, 0, 0, 0)
                if fourth_d[y][x] == 1:
                    canvas.SetPixel(fourth_start_w + x, fourth_start_h + y, 0, 0, 0)

    
    def display_temp(self, width, canvas):
        has_first, has_second, has_third = False, False, False
        air_temp = str(self.data['airTemp'])
        first_char, second_char, third_char, fourth_char = '', '', '', anim.CLOCK_NUMS[int(air_temp[-1])]
        deg = anim.SYMBOLS['DEGREE']

        if len(air_temp) == 2:
            has_third = True
            if air_temp[0] == '-':
                third_char = anim.SYMBOLS['NEG']
            else:
                third_char = anim.CLOCK_NUMS[int(air_temp[0])]
        elif len(air_temp) == 3:
            third_char = anim.CLOCK_NUMS[int(air_temp[-2])]
            has_second, has_third = True, True
            if air_temp[0] == '-':
                second_char = anim.SYMBOLS['NEG']
            else:
                second_char = anim.CLOCK_NUMS[int(air_temp[0])]
        elif len(air_temp) == 4:
            third_char = anim.CLOCK_NUMS[int(air_temp[-2])]
            second_char = anim.CLOCK_NUMS[int(air_temp[-3])]
            has_first, has_second, has_third = True, True, True
            if air_temp[0] == '-':
                first_char = anim.SYMBOLS['NEG']
            else:
                first_char = anim.CLOCK_NUMS[int(air_temp[0])]
        
        first_start_w, first_start_h = width - 21, 2
        second_start_w, second_start_h = width - 17, 2
        third_start_w, third_start_h = width - 13, 2
        fourth_start_w, fourth_start_h = width - 9, 2
        deg_start_w, deg_start_h = width = width - 5, 2

        for x in range(3):
            for y in range(5):
                if has_first and first_char[y][x] == 1:
                    canvas.SetPixel(first_start_w + x, first_start_h + y, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if has_second and second_char[y][x] == 1:
                    canvas.SetPixel(second_start_w + x, second_start_h + y, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if has_third and third_char[y][x] == 1:
                    canvas.SetPixel(third_start_w + x, third_start_h + y, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if fourth_char[y][x] == 1:
                    canvas.SetPixel(fourth_start_w + x, fourth_start_h + y, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if deg[y][x] == 1:
                    canvas.SetPixel(deg_start_w + x, deg_start_h + y, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)


    def run(self):
        width = self.matrix.width
        height = self.matrix.height

        p = mp.Process(target=self.get_data, args=(self.q,))
        p.start()

        curr_state = 0
        first_r = anim.STATES[curr_state][0]
        second_r = anim.STATES[curr_state][1]
        third_r = anim.STATES[curr_state][2]
        fourth_r = anim.STATES[curr_state][3]
        fifth_r = anim.STATES[curr_state][4]

        canvas = self.matrix.CreateFrameCanvas()

        while True:
            canvas.Clear()
            if not self.q.empty():
                self.data = self.q.get()
            # 2.142 - min since early June 2023, 16.024 - max since early June 2023
            pixelHeight = height - int(float(self.data['tideHeight']) * PIXEL_MULTI) - 1
            
            if pixelHeight > 56:
                pixelHeight = 56
            if pixelHeight < 13:
                pixelHeight = 13

            for x in range(width):
                for y in range(pixelHeight, height):
                    canvas.SetPixel(x, y, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)

            first_height, second_height, third_height, fourth_height, fifth_height = (
                pixelHeight - 5,
                pixelHeight - 4,
                pixelHeight - 3,
                pixelHeight - 2,
                pixelHeight - 1,
            )

            for x in range(width):
                if first_r[x] == 1:
                    canvas.SetPixel(x, first_height, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if second_r[x] == 1:
                    canvas.SetPixel(x, second_height, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if third_r[x] == 1:
                    canvas.SetPixel(x, third_height, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if fourth_r[x] == 1:
                    canvas.SetPixel(x, fourth_height, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)
                if fifth_r[x] == 1:
                    canvas.SetPixel(x, fifth_height, WATER_COLOR_R, WATER_COLOR_G, WATER_COLOR_B)

            curr_state = (curr_state + 1) % 5
            first_r = anim.STATES[curr_state][0]
            second_r = anim.STATES[curr_state][1]
            third_r = anim.STATES[curr_state][2]
            fourth_r = anim.STATES[curr_state][3]
            fifth_r = anim.STATES[curr_state][4]

            self.display_time(width, height, canvas, func.get_time())
            self.display_temp(width, canvas)

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(0.5)


# Main function
if __name__ == "__main__":
    tide = Tide()
    if not tide.process():
        tide.print_help()
