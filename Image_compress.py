import numpy as np
from PIL import Image
from Transformer import *


class jpeg:
    def set_image(self, filename):
        self.filename = filename
        self.img = Image.open(self.filename)
        self.img.convert("RGB")
        self.img_m = np.asarray(self.img)
        self.heigh, self.width = self.img_m.shape[0], self.img_m.shape[1]
        self.raw_heigh, self.raw_width = self.img_m.shape[0], self.img_m.shape[1]
        self.check_and_fill()

    def check_and_fill(self):
        if self.raw_heigh % 8 != 0 or self.raw_width % 8 != 0:
            ph = (8 - self.raw_heigh % 8) if self.raw_heigh % 8 != 0 else 0
            pw = (8 - self.raw_width % 8) if self.raw_width % 8 != 0 else 0
            M = np.empty((self.raw_heigh + ph, self.raw_width + pw, 3))
            for i in range(3):
                M[:, :, i] = np.pad(self.img_m[:, :, i], ((0, ph), (0, pw)), "mean")
            self.img_m = M
            if self.raw_heigh % 8 != 0:
                self.heigh = self.raw_heigh + ph
            if self.raw_width % 8 != 0:
                self.width = self.raw_width + pw

    def __init__(self):
        self.transformer = new_Transformer()
        self.qy = np.array([
            [16, 11, 10, 16, 24, 40, 51, 61],
            [12, 12, 14, 19, 26, 58, 60, 55],
            [14, 13, 16, 24, 40, 57, 69, 56],
            [14, 17, 22, 29, 51, 87, 80, 62],
            [18, 22, 37, 56, 68, 109, 103, 77],
            [24, 35, 55, 64, 81, 104, 113, 92],
            [49, 64, 78, 87, 103, 121, 120, 101],
            [72, 92, 95, 98, 112, 100, 103, 99]
        ])
        self.qc = np.array([
            [17, 18, 24, 47, 99, 99, 99, 99],
            [18, 21, 26, 66, 99, 99, 99, 99],
            [24, 26, 56, 99, 99, 99, 99, 99],
            [47, 66, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99]
        ])
        self.zig_m = np.array([
            0, 1, 8, 16, 9, 2, 3, 10,
            17, 24, 32, 25, 18, 11, 4, 5,
            12, 19, 26, 33, 40, 48, 41, 34,
            27, 20, 13, 6, 7, 14, 21, 28,
            35, 42, 49, 56, 57, 50, 43, 36,
            29, 22, 15, 23, 30, 37, 44, 51,
            58, 59, 52, 45, 38, 31, 39, 46,
            53, 60, 61, 54, 47, 55, 62, 63
        ])
        self.zag_m = np.array([
            0, 1, 5, 6, 14, 15, 27, 28,
            2, 4, 7, 13, 16, 26, 29, 42,
            3, 8, 12, 17, 25, 30, 41, 43,
            9, 11, 18, 24, 31, 40, 44, 53,
            10, 19, 23, 32, 39, 45, 52, 54,
            20, 22, 33, 38, 46, 41, 55, 60,
            21, 34, 37, 47, 50, 56, 59, 61,
            35, 36, 48, 49, 57, 58, 62, 63

        ])

    def to_ycbcr(self, r, g, b):
        y = 0.299 * r + 0.587 * g + 0.114 * b
        cb = 0.5643 * (b - y) + 128
        cr = 0.7133 * (r - y) + 128
        return y, cb, cr

    def to_rgb(self, y, cb, cr):
        r = y + 1.402 * (cr - 128)
        g = y - 0.344 * (cb - 128) - 0.714 * (cr - 128)
        b = y + 1.772 * (cb - 128)
        return r, g, b

    def to_area(self, matrix):
        h, w = matrix.shape[0], matrix.shape[1]
        strides = matrix.itemsize * np.array([w * 8, 8, w, 1])
        return np.lib.stride_tricks.as_strided(matrix, shape=(h // 8, w // 8, 8, 8), strides=strides)

    def mix_area(self, matrix):
        h, w = matrix.shape[0], matrix.shape[1]
        table = np.arange(h * w * 64).reshape((h * 8, w * 8))
        table = self.to_area(table)
        res = np.zeros(h * w * 64)
        for i in range(h):
            for j in range(w):
                for ii in range(8):
                    for jj in range(8):
                        res[table[i, j, ii, jj]] = matrix[i, j, ii, jj]

        return res.reshape(h * 8, w * 8)

    def encode(self, ratio=0.8):
        h, w = self.heigh // 8, self.width // 8
        r = self.img_m[:, :, 0]
        g = self.img_m[:, :, 1]
        b = self.img_m[:, :, 2]

        y, cb, cr = self.to_ycbcr(r, g, b)

        y_m = self.transform(self.to_area(y), "qy")
        cb_m = self.transform(self.to_area(cb), "qc")
        cr_m = self.transform(self.to_area(cr), "qc")

        ratio = int(ratio * 63)
        self.y = np.zeros((h, w, ratio))
        self.cb = np.zeros((h, w, ratio))
        self.cr = np.zeros((h, w, ratio))

        for i in range(y_m.shape[0]):
            for j in range(y_m.shape[1]):
                self.y[i, j] = self.zig(y_m[i, j])[:ratio]
                self.cb[i, j] = self.zig(cb_m[i, j])[:ratio]
                self.cr[i, j] = self.zig(cr_m[i, j])[:ratio]

    def transform(self, matrix, mode):
        h, w = matrix.shape[0], matrix.shape[1]
        m = []
        for i in range(h):
            row = []
            for j in range(w):
                row.append(self.quantize(self.dct(matrix[i, j]), mode))
            m.append(row)
        return np.asarray(m)

    def decode(self):
        h, w = self.heigh // 8, self.width // 8
        d_y = np.zeros((h, w, 8, 8))
        d_cb = np.zeros((h, w, 8, 8))
        d_cr = np.zeros((h, w, 8, 8))
        for i in range(h):
            for j in range(w):
                d_y[i, j] = (self.idct(self.inverse_quantize(
                    self.zag(self.padding(self.y[i, j])).reshape((8, 8)), mode="qy")))
                d_cb[i, j] = (self.idct(self.inverse_quantize(
                    self.zag(self.padding(self.cb[i, j])).reshape((8, 8)), mode="qc")))
                d_cr[i, j] = (self.idct(self.inverse_quantize(
                    self.zag(self.padding(self.cr[i, j])).reshape((8, 8)), mode="qc")))
        r, g, b = self.to_rgb(d_y, d_cb, d_cr)
        self.compressed_img_m = np.asarray([self.mix_area(r), self.mix_area(g), self.mix_area(b)])
        ir = Image.fromarray(self.mix_area(r)[:self.raw_heigh, :self.raw_width]).convert("L")
        ig = Image.fromarray(self.mix_area(g)[:self.raw_heigh, :self.raw_width]).convert("L")
        ib = Image.fromarray(self.mix_area(b)[:self.raw_heigh, :self.raw_width]).convert("L")
        self.compressed_img = Image.merge("RGB", (ir, ig, ib))

    def zig(self, matrix):
        m = matrix.reshape(64)
        ziged = np.zeros(64)
        for i in range(64):
            ziged[i] = m[self.zig_m[i]]
        return ziged

    def zag(self, matrix):
        m = matrix.reshape(64)
        zaged = np.zeros(64)
        for i in range(64):
            zaged[i] = m[self.zag_m[i]]
        return zaged

    def quantize(self, matrix, mode):
        quantized_matrix = matrix
        if mode == "qy":
            quantized_matrix = np.round(quantized_matrix / self.qy)
        if mode == "qc":
            quantized_matrix = np.round(quantized_matrix / self.qc)
        return np.asarray(quantized_matrix)

    def inverse_quantize(self, matrix, mode):
        inverse_quantized_matrix = matrix
        if mode == "qy":
            inverse_quantized_matrix *= self.qy
        if mode == "qc":
            inverse_quantized_matrix *= self.qc
        return np.asarray(inverse_quantized_matrix)

    def dct(self, matrix):
        return self.transformer.DCT(matrix)

    def idct(self, matrix):
        return self.transformer.IDCT(matrix)

    @staticmethod
    def padding(matrix):
        return np.pad(matrix, (0, 64 - (len(matrix) % 64)), constant_values=(0, 0))

    def get_compressed_img(self):
        return self.compressed_img

    def get_MSE(self):
        mse = 0
        raw = [0, 0, 0]
        for i in range(3):
            raw[i] = np.asarray(self.img_m[:, :, i])
            mse += np.sum((raw[i] - self.compressed_img_m[i]) ** 2)

        mse /= (self.img_m.shape[0] * self.img_m.shape[1] * 3)
        return float(mse)
