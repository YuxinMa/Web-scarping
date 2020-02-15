import os, re
import subprocess


class Image_pro(object):
    def __init__(self):
        self.threshold = 200
        self.box = (2, 2, 138, 38)
        self.clean_k = 1

    def main(self, IMG):
        ## Issue 1
        tmp1 = self.binarizing(IMG, self.threshold)
        tmp2 = self.depoint(tmp1)
        tmp3 = tmp2.crop(self.box)
        self.clean_scatter(tmp3, k=self.clean_k).save('test.jpg')
        return self.get_Text()


    def binarizing(self, img, threshold):
        img = img.convert("L")  # 转灰度
        img = img.point(lambda x: 0 if x < threshold else 255)
        return img

    def depoint(self, img):
        pixdata = img.load()
        w, h = img.size
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                count = 0
                if pixdata[x, y - 1] > 245:  # 上
                    count = count + 1
                if pixdata[x, y + 1] > 245:  # 下
                    count = count + 1
                if pixdata[x - 1, y] > 245:  # 左
                    count = count + 1
                if pixdata[x + 1, y] > 245:  # 右
                    count = count + 1
                if pixdata[x - 1, y - 1] > 245:  # 左上
                    count = count + 1
                if pixdata[x - 1, y + 1] > 245:  # 左下
                    count = count + 1
                if pixdata[x + 1, y - 1] > 245:  # 右上
                    count = count + 1
                if pixdata[x + 1, y + 1] > 245:  # 右下
                    count = count + 1
                if count > 4:
                    pixdata[x, y] = 255
        return img

    def clean_scatter(self, img, k):
        a, b = img.size
        img2 = img.load()
        for i in range(k, a - k):
            for j in range(k, b - k):
                if img2[i, j] == 0 and img2[i, j - k] == 255 and img2[i, j + k] == 255:
                    img2[i, j] = 255

                if img2[i, j] == 0 and img2[i - k, j] == 255 and img2[i + k, j] == 255:
                    img2[i, j] = 255
        return img

    def get_Text(self):
        p = subprocess.Popen(['tesseract', 'test.jpg', 'output', '-psm', '7'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

        f = open('output.txt', 'r')
        tmp2 = re.findall('[A-z, 0-9]{4}', f.read())
        return tmp2[0].strip() if tmp2 else 0
