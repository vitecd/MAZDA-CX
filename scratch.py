import sqlite3
import struct
import pygame
pygame.init()
conn = sqlite3.connect('example.db')
cur  = conn.cursor()
c_read = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS "
			"sprites (address integer, width integer, heigth integer, depth integer)")
conn.commit()

dump_len = 0

pal_bit = [1,2,4,8,16]
pal_count = 0

scr_width  = 480
scr_height = 272

db_recs = 0
db_rec  = 0

size = (scr_width,scr_height)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("MAZDA")
screen.fill(pygame.color.THECOLORS["green"])
pygame.display.flip()

with open("grayscale.act", "rb") as pal:
	pp = []
	for i in range(256):
		t1 = bytearray(pal.read(1))
		t2 = bytearray(pal.read(1))
		t3 = bytearray(pal.read(1))
		pp.append([t1[0],t2[0],t3[0]])

with open("lh28f640_mazda_cx7_457911-8580_", "rb") as bin:
	dump = bin.read()
	dump_len = bin.tell()

c_read.execute("SELECT COUNT (*) FROM sprites")
db_recs = c_read.fetchone()[0]

done = False
spr_address = 0
spr_width   = 1
spr_height  = 1

clock = pygame.time.Clock()

def read_db(sprite):
	c_read.execute("SELECT * FROM sprites")
	rows = c_read.fetchall()
	sprite.width   = rows[db_rec][1]
	sprite.height  = rows[db_rec][2]
	sprite.address = rows[db_rec][0]
	sprite.deep    = rows[db_rec][3]
	cls()
	return

def cls():
	spr_s = pygame.Surface((scr_width - 81, 272))
	spr_s.fill(pygame.color.THECOLORS["green"])
	screen.blit(spr_s, (0, 0))
	return

class Sprite():
	def __init__(self):
		self.address = 0
		self.height  = 1
		self.width   = 1
		self.deep    = 1
		self.used    = 0

	def draw(self):
		self.used    = 0
		a = self.address

		if self.deep == 1:
			for y in range(self.height):
				b = 7
				for x in range(self.width):
					t = bytearray(dump[a])
					what = t[0]

					if (1<<b) & what:
						pygame.draw.rect(screen, pp[255], (x, y, 1, 1))
					else:
						pygame.draw.rect(screen, pp[0],   (x, y, 1, 1))
					if b>0:
						b -= 1
					else:
						b  = 7
						a += 1
						self.used += 1
		elif self.deep == 4:
			for y in range(self.height):
				x = 0
				while x < self.width:
					t = bytearray(dump[a])
					what = t[0]
					pygame.draw.rect(screen, pp[what&240],     (x, y, 1, 1))
					x += 1
					a += 1
					self.used += 1
					pygame.draw.rect(screen, pp[(what&15)<<4], (x, y, 1, 1))
					x += 1

		elif self.deep == 8:
			for y in range(self.height):
				for x in range(self.width):
					t = bytearray(dump[a])
					what = t[0]
					a += 1
					self.used += 1
					pygame.draw.rect(screen, pp[what], (x, y, 1, 1))
		print ("used " + str(self.used))

	def update(self):
		return

class Pallet():
	def __init__(self):
		self.colors = 1

	def draw(self):
		pal_s = pygame.Surface((81,81))
		pal_s.fill(pygame.color.THECOLORS["black"])

		for x in range(16):
			for y in range(16):
				i = x+y*16
				color = (pp[i][0],pp[i][1],pp[i][2],0)
#				print(color)
				pygame.draw.rect(pal_s, (color), (1+(x*5), 1+(y*5), 4, 4))
		screen.blit(pal_s, (scr_width - 81, 0))

def update(self):
		return

pall = Pallet()
spr  = Sprite()
cur.execute("SELECT * FROM sprites")
if db_recs>0: db_rec = db_recs-1
read_db(spr)

pall.draw()
addr = 0x398B20
pygame.key.set_repeat(300,50)

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			cur.close()
			c_read.close()
			conn.close()
			print ("bd closed")
			done = 1
#		if event.type == pygame.MOUSEBUTTONDOWN:
#			mouse_state = 1
#			pygame.mouse.set_pos(mouse_x,mouse_y + 1)
#		else:
#			mouse_state = 0
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_PAGEUP:
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					if db_rec > 0:
						db_rec -= 1
						read_db(spr)
						spr_address = spr.address
				else:
					print spr.used
					if (spr.address-spr.used) >= 0:
						spr.address -= spr.used
					else:
						spr.address  = 0
			if event.key == pygame.K_PAGEDOWN:
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					if db_rec+1 < db_recs:
						db_rec += 1
						read_db(spr)
						spr_address = spr.address
				else:
					spr.address += spr.used
			if event.key == pygame.K_1:
				spr.deep = 1
			if event.key == pygame.K_4:
				spr.deep = 4
			if event.key == pygame.K_8:
				spr.deep = 8
			if event.key == pygame.K_LEFT:                    # left
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					if spr.deep == 1:
						if spr.width>8:
							if spr.width%8:
								spr.width = spr.width//8*8
								if spr.width > 8:
									spr.width -= 8
							else:
								spr.width -= 8
					elif spr.deep == 4:
						if spr.width>2:
							if spr.width%2:
								spr.width = spr.width//2*2
								if spr.width > 2:
									spr.width -= 2
							else:
								spr.width -= 2
					elif spr.deep == 8:
						if spr.width > 1:
							spr.width -= 1
				elif spr.address > 1:
					spr.address -= 1
			if event.key == pygame.K_RIGHT:                   # right
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					if spr.deep == 1:
						if spr.width%8:
							spr.width = spr.width//8*8+8
						else:
							spr.width += 8
					elif spr.deep == 4:
						if spr.width%2:
							spr.width = spr.width//2*2+2
						else:
							spr.width += 2
					elif spr.deep == 8:
						spr.width += 1
				else:
					spr.address += 1
			if event.key == pygame.K_UP:
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					if spr.height > 1:
						spr.height -= 1
						# spr.height  = spr_height
				elif spr.address > spr.width:
					spr.address -= spr.width
					# spr.address = spr_address
			if event.key == pygame.K_DOWN:
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					spr.height += 1
					# spr.height  = spr_height
				else:
					spr.address += spr.width
					# spr.address = spr_address
			if event.key == pygame.K_p:
				if pal_count != 4:
					pal_count += 1
				else:
					pal_count = 0
			if event.key == pygame.K_d:
				spr.width /=2
				# spr.width  = spr_width
			if event.key == pygame.K_m:
				spr.width *=2
				# spr.width  = spr_width
			if event.key == pygame.K_RETURN:
				cur.execute("INSERT INTO sprites VALUES ("+str(spr.address)+","+str(spr.width)+","+str(spr.height)+","+str(spr.deep)+")")
				conn.commit()
				print ("inserted")
				if spr.deep == 8:
					spr.deep = 1
					spr.width *=2
				elif spr.deep == 1:
					spr.deep = 8
					spr.width /=2
				spr.address += spr.used
			if event.key == pygame.K_u:
				c_read.execute("SELECT COUNT (*) FROM sprites")
				db_recs = c_read.fetchone()[0]
			cls()
			spr.draw()

	pygame.display.set_caption("Adr: 0x"+"{0:X}".format(spr.address)+" : "+str(spr.width)+" x "+str(spr.height)+"  "+str(spr.deep) + " bit " +str((dump_len-spr.address)/(dump_len/100)) + "%")
	pygame.display.update()
	clock.tick(50)

pygame.quit()