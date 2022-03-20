#!/usr/bin/env python3

#	This file is part of PulseEqualizerGui for Kodi.
#	
#	Copyright (C) 2021 wastis    https://github.com/wastis/PulseEqualizerGui
#
#	PulseEqualizerGui is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#
import sys
import os
import json
import math

sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

from helper import log
from sound import SpecManager

from PIL import Image, ImageDraw, ImageFont


with Image.new("RGBA",(1700, 700),(0,0,0,0)) as im:
	#im.load("/home/user/Script/kodi/develop/script.pulseequalizer.gui/debug/resources/skins/Default/media/equalizer-panel.png")
	
	h = im.size[1] - 55
	w = im.size[0] - 105
	zero_y = int(h / 2)
	zero_x = 100
	scale = h / 40
	
	xscale = w / 2.5
	
	col= (255,255,255,255)
	fnt = ImageFont.truetype("FreeMono.ttf", 35)
	draw = ImageDraw.Draw(im)
	
	draw.text((5,5), "[dB]", font=fnt, fill=col, stroke_width=2)
	
	for i in [4,8,12,16]:
		ch = i * scale
		draw.line((zero_x, zero_y + ch , zero_x + w, zero_y + ch ), fill=col, width = 2)
		draw.line((zero_x, zero_y - ch , zero_x + w, zero_y - ch ), fill=col, width = 2)
		
		font_width, font_height = fnt.getsize(str(i))
		draw.text((zero_x - font_width - 15,zero_y - ch - font_height / 2), str(i), font=fnt, fill=col,stroke_width=2)
		
		font_width, font_height = fnt.getsize("-"+str(i))
		draw.text((zero_x - font_width - 15,zero_y + ch - font_height / 2), "-"+str(i), font=fnt, fill=col, stroke_width=2)

	for i in [100,200,300,400,500,600,700,800,900,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,20000,30000]:
		x = (math.log10(i) - 2) * xscale + zero_x
		draw.line((x, 5, x, h), fill=col, width = 2)

	for t in ["100Hz","500Hz","1kHz","5kHz","10kHz","20kHz"]:
		i = int(t[:-2].replace("k","000"))
		x = (math.log10(i) - 2) * xscale + zero_x
		draw.text((x ,h + 10), t, font=fnt, fill=col, stroke_width=2)
		
	draw.line((zero_x, zero_y, zero_x + w, zero_y), fill=col, width = 5)
	draw.line((zero_x, 5, zero_x + w, 5), fill=col, width = 5)
	draw.line((zero_x, h, zero_x + w, h), fill=col, width = 5)
	draw.line((zero_x, 5, zero_x, h), fill=col, width = 5)
	draw.line((zero_x + w, 5, zero_x + w, h), fill=col, width = 5)
	
	spec = SpecManager()
	spec.select_spec("bose")
	
	coords = []
	for f,v in spec.cur_spec.freq_db:
		if f < 100: continue
		if f > 25000: break

		xl = (math.log10(f) - 2) * xscale + zero_x
		yl = math.log10(1 / v) * 20
		if yl > 20: yl = 20
		yl = zero_y - yl * scale
		
		coords.append((xl, yl))
	
	if coords:
		x1, y1 = coords[0]
		for x2,y2 in coords[1:]:
			draw.line((x1, y1, x2, y2),fill=(4,35,40,128), width = 7)
			x1 = x2
			y1 = y2
	
		x1, y1 = coords[0]
		for x2,y2 in coords[1:]:
			draw.line((x1, y1, x2, y2),fill=(15,133,165,255), width = 5)
			x1 = x2
			y1 = y2
	
	
	# write to stdout
	im.save("/home/user/Script/kodi/develop/script.pulseequalizer.gui/debug/resources/skins/Default/media/equalizer-panel_2.png", "PNG")
