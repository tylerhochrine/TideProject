#!/usr/bin/env python
from samplebase import SampleBase
import time
import multiprocessing as mp
import Functions as func
import Animation as anim


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

                if self.data['tideHeight'] < 3:
                    self.data['tideHeight'] = 3
                elif self.data['tideHeight'] > 15:
                    self.data['tideHeight'] = 15
                
            pixelHeight = height - int(float(self.data['tideHeight']) * 4)

            for x in range(width):
                for y in range(pixelHeight + 3, height):
                    canvas.SetPixel(x, y, 0, 157, 196)

            first_height, second_height, third_height, fourth_height, fifth_height = (
                pixelHeight - 2,
                pixelHeight - 1,
                pixelHeight,
                pixelHeight + 1,
                pixelHeight + 2,
            )

            for x in range(width):
                if first_r[x] == 1:
                    canvas.SetPixel(x, first_height, 0, 157, 196)
                if second_r[x] == 1:
                    canvas.SetPixel(x, second_height, 0, 157, 196)
                if third_r[x] == 1:
                    canvas.SetPixel(x, third_height, 0, 157, 196)
                if fourth_r[x] == 1:
                    canvas.SetPixel(x, fourth_height, 0, 157, 196)
                if fifth_r[x] == 1:
                    canvas.SetPixel(x, fifth_height, 0, 157, 196)

            curr_state = (curr_state + 1) % 5
            first_r = anim.STATES[curr_state][0]
            second_r = anim.STATES[curr_state][1]
            third_r = anim.STATES[curr_state][2]
            fourth_r = anim.STATES[curr_state][3]
            fifth_r = anim.STATES[curr_state][4]

            self.display_time(width, height, canvas, func.get_time())

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(0.5)


# Main function
if __name__ == "__main__":
    tide = Tide()
    if not tide.process():
        tide.print_help()
