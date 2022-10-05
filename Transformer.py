import numpy as np
import math


class Transformer:  # 作業版本 效率較差
    def __init__(self, matrix):
        self.matrix = matrix
        self.N = self.matrix.shape[0]
        self.transformed_matrix = np.zeros_like(self.matrix, dtype=np.float_)

    def DCT_transform(self, i, j):
        sigma = 0
        for y in range(self.N):
            for x in range(self.N):
                tmp = self.matrix[y, x]
                tmp *= math.cos(math.pi * (2 * y + 1) * i / (2. * self.N))
                tmp *= math.cos(math.pi * (2 * x + 1) * j / (2. * self.N))
                sigma += tmp

        ci, cj = 1.0, 1.0

        if i == 0:
            ci = 1 / np.sqrt(2)
        if j == 0:
            cj = 1 / np.sqrt(2)

        return (1 / np.sqrt(2 * self.N)) * ci * cj * sigma

    def IDCT_transform(self, i, j):
        sigma = 0
        for y in range(self.N):
            for x in range(self.N):
                tmp = self.matrix[y, x]
                if y == 0:
                    tmp /= np.sqrt(2)
                if x == 0:
                    tmp /= np.sqrt(2)
                tmp *= math.cos(math.pi * (2 * i + 1) * y / (2. * self.N))
                tmp *= math.cos(math.pi * (2 * j + 1) * x / (2. * self.N))
                sigma += tmp

        return (2 / np.sqrt(self.N * self.N)) * sigma

    def start_DCT_trans(self):
        for i in range(self.N):
            for j in range(self.N):
                self.transformed_matrix[i, j] = self.DCT_transform(i, j)

    def start_IDCT_trans(self):
        for i in range(self.N):
            for j in range(self.N):
                self.transformed_matrix[i, j] = self.IDCT_transform(i, j)

    def get_transformed_matrix(self):
        return self.transformed_matrix


class new_Transformer:  # 期末版本 使用8*8效率較佳
    def __init__(self):
        self.dct_matrix = np.zeros((8, 8))
        for i in range(8):
            c = 0
            if i == 0:
                c = np.sqrt(1 / 8)
            else:
                c = np.sqrt(2 / 8)
            for j in range(8):
                self.dct_matrix[i, j] = c * np.cos(np.pi * i * (2 * j + 1) / 16)

    def DCT(self, matrix):
        transformed = np.dot(self.dct_matrix, matrix)
        transformed = np.dot(transformed, np.transpose(self.dct_matrix))
        return transformed

    def IDCT(self, matrix):
        transformed = np.dot(np.transpose(self.dct_matrix), matrix)
        transformed = np.dot(transformed, self.dct_matrix)
        return transformed


