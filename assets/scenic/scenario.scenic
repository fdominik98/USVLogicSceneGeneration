
class Sea(Object):
    width: 10000
    length: 10000
    height: 0.01
    position: (0,0,0)
    color: [150/255,220/255,250/255]

class Ship(Object):
    color : [150/255,0/255,0/255]

workspace = Workspace(RectangularRegion(0@0, 0, 10000, 10000))

sea = new Sea

ship_radius = 200

ship1 = new Ship on sea
ship1_region = CircularRegion(ship1.position, ship_radius)
ship2 = new Ship on sea
ship2_region = CircularRegion(ship2.position, ship_radius)

# Add both ships to the scene
ego = ship1
require distance from ship1 to ship2 > 1000
require distance from ship1 to ship2 < 1100 