import numpy as np

pi = np.pi


def bicubic_interpolation(im, x_out, y_out, width, height):
    y_f = int(y_out)
    x_f = int(x_out)
    p = y_out - y_f
    q = x_out - x_f
    if y_f == 0:
        p = 0
    if y_f >= height - 1:
        y_f = height - 1
        return (1 - q) * im[y_f, np.mod(x_f, width)] + q * im[y_f, np.mod(x_f + 1, width)]
    else:
        return (1 - p) * (1 - q) * im[y_f, np.mod(x_f, width)] + \
               (1 - p) * q * im[y_f, np.mod(x_f + 1, width)] + \
               p * (1 - q) * im[y_f, np.mod(x_f, width)] + \
               p * q * im[y_f, np.mod(x_f + 1, width)]


class viewportSampling():
    def __init__(self, ref, dis, lon, lat, FOV):
        super(viewportSampling, self).__init__()
        assert ref.shape == dis.shape
        self.ref = ref.squeeze(dim=0)
        self.dis = dis.squeeze(dim=0)
        self.lon = lon
        self.lat = lat
        self.FOV = FOV

    def rotationMatrix(self):
        R = np.array([[np.cos(self.lon), np.sin(self.lon) * np.sin(self.lat), np.sin(self.lon) * np.cos(self.lat)], \
                      [0, np.cos(self.lat), - np.sin(self.lat)], \
                      [-np.sin(self.lon), np.cos(self.lon) * np.sin(self.lat), np.cos(self.lon) * np.cos(self.lat)]])
        return R

    def sampling(self):
        R = viewportSampling.rotationMatrix(self)
        height = self.ref.shape[0]
        width = self.ref.shape[1]
        F_h = F_v = self.FOV
        viewportSize = np.floor(self.FOV / (2 * np.pi) * width)
        viewport_ref = np.zeros((int(viewportSize), int(viewportSize)))
        viewport_dis = np.zeros((int(viewportSize), int(viewportSize)))
        for i in range(int(viewportSize) - 1):
            for j in range(int(viewportSize) - 1):
                u = (j + 0.5) * 2 * np.tan(F_h / 2) / viewportSize
                v = (i + 0.5) * 2 * np.tan(F_v / 2) / viewportSize

                x1 = u - np.tan(F_h / 2)
                y1 = -v + np.tan(F_v / 2)
                z1 = 1.0

                r = np.sqrt(x1 ** 2 + y1 ** 2 + z1 ** 2)

                sphere_coords = [x1 / r, y1 / r, z1 / r]
                rotated_sphere_coords = np.matmul(R, sphere_coords)

                x = rotated_sphere_coords[0]
                y = rotated_sphere_coords[1]
                z = rotated_sphere_coords[2]

                theta = np.arccos(y)
                phi = np.arctan2(x, z)

                x_out = width * phi / (2 * np.pi)
                y_out = height * theta / np.pi

                viewport_ref[i, j] = bicubic_interpolation(self.ref, x_out, y_out, width, height)
                viewport_dis[i, j] = bicubic_interpolation(self.dis, x_out, y_out, width, height)

        return viewport_ref, viewport_dis

    def getcoords3(self, anglex, angley):
        lat = - self.lat
        lon = self.lon
        faceSizex = 2 * np.tan(anglex / 2)
        faceSizey = 2 * np.tan(angley / 2)
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        point = np.hstack((x, y, z))
        vector1 = np.array([-np.sin(lon), np.cos(lon), 0])
        vector2 = np.array([np.sin(lat) * np.cos(lon), np.sin(lat) * np.sin(lon), -np.cos(lat)])
        coords = np.zeros((3, 4))
        coords[:, 0] = point - vector1 * faceSizex / 2 - vector2 * faceSizey / 2
        coords[:, 1] = point + vector1 * faceSizex / 2 - vector2 * faceSizey / 2
        coords[:, 2] = point - vector1 * faceSizex / 2 + vector2 * faceSizey / 2
        coords[:, 3] = point + vector1 * faceSizex / 2 + vector2 * faceSizey / 2
        return coords

    def sampling2(self):
        height = self.ref.shape[0]
        width = self.ref.shape[1]
        FOV = self.FOV
        viewportSize = np.floor(FOV / (2 * pi) * width)
        anglex = (180 * viewportSize / height) * pi / 180
        angley = (180 * viewportSize / width) * pi / 180
        coords = viewportSampling.getcoords3(self, anglex, angley)
        viewport_ref = np.zeros((int(viewportSize), int(viewportSize)))
        viewport_dis = np.zeros((int(viewportSize), int(viewportSize)))
        for i in range(int(viewportSize) - 1):
            for j in range(int(viewportSize) - 1):
                c = 1.0 * i / viewportSize
                d = 1.0 * j / viewportSize

                x = (1 - c) * (1 - d) * coords[0, 0] + c * (1 - d) * coords[0, 1] + \
                    (1 - c) * d * coords[0, 2] + c * d * coords[0, 3]
                y = (1 - c) * (1 - d) * coords[1, 0] + c * (1 - d) * coords[1, 1] + \
                    (1 - c) * d * coords[1, 2] + c * d * coords[1, 3]
                z = (1 - c) * (1 - d) * coords[2, 0] + c * (1 - d) * coords[2, 1] + \
                    (1 - c) * d * coords[2, 2] + c * d * coords[2, 3]

                r = np.sqrt(x**2 + y**2 + z**2)
                theta = np.arcsin(z / r)
                if x < 0 and y <= 0:
                    phi = np.arctan(y / x) - pi
                elif x < 0 and y > 0:
                    phi = np.arctan(y / x) + pi
                else:
                    phi = np.arctan(y / x)
                y_out = (pi / 2 - theta) * height / pi
                x_out = phi * width / 2 / pi
                viewport_ref[j, i] = bicubic_interpolation(self.ref, x_out, y_out, width, height)
                viewport_dis[j, i] = bicubic_interpolation(self.dis, x_out, y_out, width, height)

        return viewport_ref, viewport_dis

    # def sampling_v2(self):
    #     R = viewportSampling.rotationMatrix(self)
    #     height = self.ref.shape[0]
    #     width = self.ref.shape[1]
    #     F_h = F_v = self.FOV
    #     viewportSize = np.floor(self.FOV / (2 * np.pi) * width)
    #     viewport_ref = np.zeros((int(viewportSize), int(viewportSize)))
    #     viewport_dis = np.zeros((int(viewportSize), int(viewportSize)))
    #     index = np.arange(0, 160, 1).reshape([-1, 160])
    #     index = (index + 0.5) * 2 * np.tan(F_h / 2) / viewportSize
    #     x1 = index - np.tan(F_h / 2)
    #     y1 = -index + np.tan(F_v / 2)
    #     z1 = np.ones(index.shape[0])
    #     r = np.sqrt(x1 ** 2 + y1 ** 2 + z1 ** 2)
    #
    #     sphere_coords = np.concatenate((x1 / r, y1 / r, z1 / r))
    #     rotated_sphere_coords = np.matmul(R, sphere_coords)
    #     theta = np.arccos(rotated_sphere_coords[1, :]).reshape([-1, 160])
    #     phi = np.arctan2(rotated_sphere_coords[0, :], rotated_sphere_coords[2, :]).reshape([-1, 160])
    #
    #     x_out = width * phi / (2 * np.pi)
    #     y_out = height * theta / np.pi
    #
    #     y_f = y_out.astype(int).reshape([-1, 160])
    #     x_f = x_out.astype(int).reshape([-1, 160])
    #     p = y_out - y_f
    #     q = x_out - x_f
    #     p[y_f == 0] = 0
    #     y_f[y_f >= height] = height
    #
