import pygame as pg
from random import uniform
from vehicle import Vehicle


class Boid(Vehicle):

    # CONFIG
    debug = True  # Отображение векторов движения
    # green - скорость (velocity)
    # blue - необходимое направление (steering)
    # red - ускорение (acceleration)
    min_speed = 0
    max_speed = 0.1
    max_force = 1  # Предположу что это тяга xD
    max_turn = 2  # Насколько быстро поворачивает и т.д.
    perception = 60  # На каком расстоянии замечают друг друга
    crowding = 30  # Какое расстояние удерживают в рое
    can_wrap = False  # Границы-телепорты
    edge_distance_pct = 3  # Кажется, границы самих объектов(не точно)
    ###############

    def __init__(self):
        Boid.set_boundary(Boid.edge_distance_pct)
        startpozx = 100
        startpozy = 100
        destposx = 200
        destposy = 200
        start_velocity = pg.math.Vector2(destposx * Boid.max_speed,destposy * Boid.max_speed
            )
        # Randomize starting position and velocity
        start_position = pg.math.Vector2(startpozx,startpozy)  # Рандомная зона спавна
            #uniform(0, Boid.max_x),
            #uniform(0, Boid.max_y))
        #start_velocity = pg.math.Vector2(
            #uniform(-1, 1) * Boid.max_speed,
            #uniform(-1, 1) * Boid.max_speed)  # Рандомная скорость

        super().__init__(start_position, start_velocity,
                         Boid.min_speed, Boid.max_speed,
                         Boid.max_force, Boid.can_wrap)

        self.rect = self.image.get_rect(center=self.position)

        self.debug = Boid.debug

    def separation(self, boids):
        steering = pg.Vector2()
        for boid in boids:
            dist = self.position.distance_to(boid.position)  # Дистанция между соседом
            if dist < self.crowding:
                steering -= boid.position - self.position  # Начинает следовать (вроде xD)
        steering = self.clamp_force(steering)
        # В теории должен тянуться после этого за другим, т.к. новый вектор движения
        return steering

    def alignment(self, boids):
        steering = pg.Vector2()
        for boid in boids:
            steering += boid.velocity
        steering /= len(boids)  # Средняя скорость (типо)
        steering -= self.velocity
        steering = self.clamp_force(steering)
        return steering / 8  # Лучше не трогать xD

    def cohesion(self, boids):  # Cohesion - сплочённость, связь
        steering = pg.Vector2()
        for boid in boids:
            steering += boid.position  # Сумма всех координат дронов
        steering /= len(boids)  # Видимо средняя координата между ними
        steering -= self.position
        steering = self.clamp_force(steering)
        return steering / 100  # Чем меньше, тем более спокойные

    def update(self, dt, boids):
        steering = pg.Vector2()

        if not self.can_wrap:
            steering += self.avoid_edge()  # Если нет телепорта через границу, то избегать её

        neighbors = self.get_neighbors(boids)
        if neighbors:  # Если кто-то есть рядом, то...

            separation = self.separation(neighbors)
            alignment = self.alignment(neighbors)
            cohesion = self.cohesion(neighbors)

            # DEBUG
            # separation *= 0
            # alignment *= 0
            # cohesion *= 0

            steering += separation + alignment + cohesion

        # steering = self.clamp_force(steering)

        super().update(dt, steering)  # Обновление экрана

    def get_neighbors(self, boids):
        neighbors = []
        for boid in boids:
            if boid != self:
                dist = self.position.distance_to(boid.position)
                if dist < self.perception:  # Perception - радиус обзора
                    neighbors.append(boid)  # Если кто-то в радиусе бота self он добавляется как попутчик
        return neighbors
