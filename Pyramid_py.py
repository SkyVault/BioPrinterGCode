def Generate_Rectangle_Matrix(size, layers, density, layer_height):
	lines = []
	cursor_x = 0
	cursor_y = 0
	cursor_z = 0

	offset_x = 40
	offset_y = 40

	direction = 1

	which = 1
	fill_spacing = density
	speed = 150

	g.begin(lines)
	
	rate = 0.00019
	Setup_Extrusion(lines, rate)
	
	# Move it up one unit
	lines.append(g.gl_create_z(cursor_z, 200))
	cursor_z += layer_height
	lines.append(g.gl_create_z(cursor_z, 200))

	# Draw out the extrusion circle
	rad = size
	for i in range(0, 4): # 10 rings of the circle
		for r in range(0, 32): # 32 = resolution
			x = (rad * math.cos(r * (2 * 3.14159) / 32)) + offset_x
			y = (rad * math.sin(r * (2 * 3.14159) / 32)) + offset_y
 
			if i == 0 and r == 0:
				lines.append(g.g1_create(x + size / 2, y + size/2, speed * 6))
			else:
				lines.append(g.g1_create(x + size / 2, y + size/2, speed))

		rad -= 0.05	
	
	lines.append("G90")
	lines.append(g.g1_create(0, 0, speed * 6))
	
	extensions = float(EXTENSIONS)
	
	layer_index = 0.0
	for layer in range(0, layers):
		
		if which == 1:
			while cursor_x < size:
				cursor_y = (direction * size / 2) + size / 2 + (extensions * direction)
				lines.append(g.g1_create(cursor_x + offset_x, cursor_y + offset_y, speed))
				cursor_x += fill_spacing
				lines.append(g.g1_create(cursor_x + offset_x, cursor_y + offset_y, speed))
				direction *= -1	
		else:
			while cursor_y < size:
				cursor_x = (direction * size / 2) + size / 2 + (extensions * direction)
				lines.append(g.g1_create(cursor_x + offset_x, cursor_y + offset_y, speed))
				cursor_y += fill_spacing
				lines.append(g.g1_create(cursor_x + offset_x, cursor_y + offset_y, speed))
				direction *= -1	
		extensions = EXTENSIONS - (1.0 * layer_index) / (1.0 * layers) * (1.0 * EXTENSIONS)

		# find the center
		# NOTE: Not doing this right now, maybe each layer we could
		# move it up to scrape the blob off
		'''
		cx, cy = g.find_center(lines)
		
		# draw tangent
		lines.append(g.g1_create(cx, cy, 200))
		lines.append(g.gl_create_z(30, 200))
		lines.append(g.gl_create_z(cursor_z, 200))
		'''

		
		# move up a layer
		lines.append(g.gl_create_z(cursor_z, 200))
		cursor_z += layer_height
		lines.append(g.gl_create_z(cursor_z, 200))

		which *= -1
		cursor_y = 0
		cursor_x = 0

		if INCREASE_EACH_LAYER and layer_index > 0:
			lines.append("M4")
			lines.append("S" + '{0:f}'.format(0.0021))	# Change the rate by a  hundredths
		if SHRINK_EACH_LAYER:
			layer_height *= 0.94
			rate *= 1.01

		# Go back to home when the part is finshed

		layer_index += 1.0

	lines.append("G1 X0 Y0 Z0 F2000")

	g.end(lines)
	return lines

