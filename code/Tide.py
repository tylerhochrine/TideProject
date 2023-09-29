#!/usr/bin/env python
from samplebase import SampleBase
import time
import multiprocessing as mp
import Functions as func
import Animation as anim


class Tide(SampleBase):
    dtmTime = ""
    tideHeight = 1
    q = mp.Queue()

    def __init__(self, *args, **kwargs):
        super(Tide, self).__init__(*args, **kwargs)
        func.wait_for_internet_connection()
        self.dtmTime, self.tideHeight = func.get_current_water_level(
            self.dtmTime, self.tideHeight
        )
        self.q.put([self.dtmTime, self.tideHeight])

    def get_tide_data(self, q):
        while True:
            self.dtmTime, self.tideHeight = func.get_current_water_level(
                self.dtmTime, self.tideHeight
            )
            self.q.put([self.dtmTime, self.tideHeight])

    def run(self):
        width = self.matrix.width
        height = self.matrix.height

        p = mp.Process(target=self.get_tide_data, args=(self.q,))
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
                self.dtmTime, self.tideHeight = self.q.get()

            pixelHeight = height - int(float(self.tideHeight) * 4)

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

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(0.5)


# Main function
if __name__ == "__main__":
    tide = Tide()
    if not tide.process():
        tide.print_help()
