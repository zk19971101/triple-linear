import numpy as np


class TriLinear:
    def __init__(self, src_point=(150, 230, 71), dim=33):
        self.src_point = src_point
        self.dim = dim

    def linear(self, dest_x, low_coordination, high_coordination):
        assert low_coordination[0] <= dest_x <= high_coordination[0], \
            f"expect {dest_x} between {low_coordination[0]} and {high_coordination[0]}, but find not!"
        alpha = (dest_x - low_coordination[0]) / (high_coordination[0] - low_coordination[0])
        return dest_x, low_coordination[1] * (1 - alpha) + high_coordination[1] * alpha

    def double_linear(self, dest_coordination, *point_list):
        assert len(point_list) == 4, "error, double_linear need 4 point!"
        c00, c01, c10, c11 = point_list
        _, y_c00_c01 = self.linear(dest_coordination[0], c00[::2], c01[::2])
        _, y_c10_c11 = self.linear(dest_coordination[0], c10[::2], c11[::2])
        _, num = self.linear(dest_coordination[1], (c00[1], y_c00_c01), (c10[1], y_c10_c11))
        return dest_coordination, num

    def triple_linear(self, dest_coordination, *point_List):
        assert len(point_List) == 8, "error, triple_linear need 8 point!"
        c000, c001, c010, c011, c100, c101, c110, c111 = point_List
        _, y_000_100_010_110 = self.double_linear(
            dest_coordination[:-1], (*c000[:2], c000[-1]), (*c100[:2], c100[-1]), (*c010[:2], c010[-1]), (*c110[:2], c110[-1]))

        _, y_001_101_011_111 = self.double_linear(
            dest_coordination[:-1], (*c001[:2], c001[-1]), (*c101[:2], c101[-1]), (*c011[:2], c011[-1]),
            (*c111[:2], c111[-1]))
        _, num = self.linear(dest_coordination[-1], (c000[-2], y_000_100_010_110), (c001[-2], y_001_101_011_111))
        return dest_coordination, num

    def get_neighbor_point(self, src_point: tuple, lut: np.array):
        """
        从三维的LUT中选择与查找point在三个维度上最接近的8个邻接点。
        :param src_point: (x, y, z)
        :param lut: shape = [1, dim, dim, dim, 3]
        :return: 8 neighbor points
        """
        step = 256. / self.dim
        src_index = [int(i//step) for i in src_point]
        neighbor_index = list(zip(src_index, [i+1 for i in src_index]))
        get_point_list = lambda index: [(i, j, k, lut[0, index, i, j, k]) for i in neighbor_index[0] for j in neighbor_index[1] for k in neighbor_index[2]]
        point_list_r = get_point_list(0)
        point_list_g = get_point_list(1)
        point_list_b = get_point_list(2)
        return step, point_list_r, point_list_g, point_list_b

    def test_linear(self):
        dest_x = 5
        lower = (1, 7)
        higher = (7, 18)
        coordination = self.linear(dest_x, lower, higher)
        print(coordination)

    def test_double_linear(self):
        c00 = (1, 1, 5)
        c01 = (5, 1, 9)
        c10 = (1, 5, 13)
        c11 = (5, 5, 28)
        a = self.double_linear((3, 3), c00, c01, c10, c11)
        print(a)

    def test_triple_linear(self):
        c000 = (1, 1, 1, 5)
        c001 = (1, 1, 7, 8)
        c010 = (1, 7, 1, 9)
        c011 = (1, 7, 7, 18)
        c100 = (7, 1, 1, 6)
        c101 = (7, 1, 7, 13)
        c110 = (7, 7, 1, 16)
        c111 = (7, 7, 7, 94)
        x = self.triple_linear((3, 5, 6), c000, c001, c010, c011, c100, c101, c110, c111)
        print(x)

    def read_lut(self, lut_txt="./IdentityLUT33.txt"):
        with open(lut_txt, 'r') as f:
            data = f.readlines()
        data = [[float(j) for j in i.split()] for i in data]
        lut = np.array(data).reshape(1, 3, self.dim, self.dim, self.dim)
        return lut


if __name__ == '__main__':
    tri_linear = TriLinear()
    tri_linear.test_triple_linear()
    lut = tri_linear.read_lut()
    step, *point_list = tri_linear.get_neighbor_point(tri_linear.src_point, lut)
    print("step", step)
    src_index = [i / step for i in tri_linear.src_point]
    r_point_list, g_point_list, b_point_list = point_list
    x = tri_linear.triple_linear(src_index, *g_point_list)
    print(x)





