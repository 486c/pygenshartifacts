import os

import cv2
import numpy as np
import pytesseract
from fuzzywuzzy import fuzz



def get_list_sum(nums: list):
    theSum = 0

    for i in nums:
        theSum += i

    return theSum


class Parser():

    def __init__(self, image):
        self.pillow_image = image
        self.opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def find_patt(self, patt):
        img_grey = cv2.cvtColor(self.opencv_image, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(img_grey, patt, cv2.TM_CCOEFF_NORMED)

        loc = np.where(res > 0.7)

        return loc


    def img_to_str(self, lang):
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        results = []

        for pattern in ['ArtParser\\Pics\\' + image_name for image_name in os.listdir('ArtParser\\Pics')]:
            founded = self.find_patt(cv2.imread(pattern, 0))

            if len(founded[0]):
                for y, x in zip(founded[0], founded[1]):
                    if y in [cords[0] for cords in results] or x in [cords[1] for cords in results]:
                        pass
                    else:
                        results.append([y, x])
            else:
                pass

        if results:
            for result in results:
                try:
                    crop_x_1 = 0
                    crop_y_1 = 0
                    crop_x_2 = self.pillow_image.size[0]
                    crop_y_2 = self.pillow_image.size[1]

                    pixel_color = self.opencv_image[result[0], result[1]]
                    pixel_color = range(get_list_sum(pixel_color) - 10, get_list_sum(pixel_color) + 10)


                    for y in reversed(range(0, result[0])):
                        if get_list_sum(list(self.opencv_image[y, result[1]])) not in pixel_color:
                            crop_y_1 = y + 3

                            break


                    for x in reversed(range(0, result[1])):
                        if get_list_sum(list(self.opencv_image[crop_y_1, x])) not in pixel_color:
                            crop_x_1 = x + 3

                            break


                    for x in range(result[1], self.pillow_image.size[0]):
                        if get_list_sum(list(self.opencv_image[crop_y_1, x])) not in pixel_color:
                            crop_x_2 = x - 3

                            break


                    for y in range(result[0], self.pillow_image.size[1]):
                        if get_list_sum(list(self.opencv_image[y, crop_x_2])) not in pixel_color:
                            crop_y_2 = y - 3

                            break
                    
                    img = self.opencv_image[
                        crop_y_1:crop_y_2,
                        crop_x_1:crop_x_2
                    ]
                
                    stats_names = [
                        'HP',
                        'Сила атаки',
                        'Защита',
                        'Мастерство стихий',
                        'Восст. энергии',
                        'Шанс крит. попадания',
                        'Крит. урон'
                    ]

                    lines = []
                    to_return = []

                    for line in [x for x in pytesseract.image_to_string(img, lang= lang).split('\n') if len(x) > 5][:7]:
                        line = line.replace('МР', 'HP').replace('НР', 'HP').replace('Силаатаки', 'Сила атаки').strip().lstrip('.')
                        
                        for stat_name in stats_names:
                            if fuzz.WRatio(stat_name, line) > 80:
                                lines.append(line)
                            elif fuzz.WRatio(stat_name, line[1:]) > 80:
                                lines.append(line)
                            elif fuzz.WRatio(stat_name, line[2:]) > 80:
                                lines.append(line)
                            else:
                                pass

                    if lines:
                        for line in lines:
                            for stat_name in stats_names:
                                if fuzz.ratio(stat_name, line.split('+')[0].strip()) > 80:
                                    to_return.append(f'{stat_name} +{line.split("+")[1].strip()}')
                                elif fuzz.ratio(stat_name, line.split('+')[0].strip()[1:]) > 80:
                                    to_return.append(f'{stat_name} +{line.split("+")[1].strip()}')
                                elif fuzz.ratio(stat_name, line.split('+')[0].strip()[2:]) > 80:
                                    to_return.append(f'{stat_name} +{line.split("+")[1].strip()}')
                                else:
                                    pass

                        if to_return:
                            return [to_return, lines]
                        else:
                            pass
                    else:
                        pass
                except Exception:
                    pass
            
            return None
        else:
            return None