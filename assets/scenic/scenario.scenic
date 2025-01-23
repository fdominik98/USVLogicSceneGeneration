

workspace = new Workspace(RectangularRegion((0,0), 3.14/2, 30000, 30000, name='sea'))
sea = workspace

ego = new Object on sea with CylinderShape(), with width 2 * 100, with length 2 * 100, with height 1
ship2 = new Object on sea with CylinderShape(), with width 2 * 100, with length 2 * 100, with height 1