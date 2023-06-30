// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

export const invertColor = (hexTripletColor: string): string => {
	let color = hexTripletColor;
	color = color.substring(1); // remove #
	let color_int = parseInt(color, 16); // convert to integer
	color_int = 0xffffff ^ color_int; // invert three bytes
	color = color_int.toString(16); // convert to hex
	color = `000000${color}`.slice(-6); // pad with leading zeros
	color = `#${color}`; // prepend #
	return color;
};

export const calculate_score = (q_time: number, time_taken: number): number => {
	return q_time / time_taken;
};

export type RGB = [number, number, number];

export const getLuminance = (rgb: RGB): number => {
	const [r, g, b] = rgb.map((v) => {
		v /= 255;
		return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
	});
	return r * 0.2126 + g * 0.7152 + b * 0.0722;
};

export const getContrast = (foregroundColor: RGB, backgroundColor: RGB) => {
	const foregroundLuminance = getLuminance(foregroundColor);
	const backgroundLuminance = getLuminance(backgroundColor);
	return backgroundLuminance < foregroundLuminance
		? (backgroundLuminance + 0.05) / (foregroundLuminance + 0.05)
		: (foregroundLuminance + 0.05) / (backgroundLuminance + 0.05);
};

export const getRgbColorFromHex = (hex: string): RGB => {
	hex = hex.slice(1);
	const value = parseInt(hex, 16);
	// skipcq: JS-C1002
	const r = (value >> 16) & 255;
	// skipcq: JS-C1002
	const g = (value >> 8) & 255;
	// skipcq: JS-C1002
	const b = value & 255;

	return [r, g, b] as RGB;
};

export const get_foreground_color = (bg_color: string): 'black' | 'white' => {
	const bg_rgb = getRgbColorFromHex(bg_color);
	const white_rgb: RGB = [255, 255, 255];
	const black_rgb: RGB = [0, 0, 0];
	const black_contrast = getContrast(black_rgb, bg_rgb);
	const white_contrast = getContrast(white_rgb, bg_rgb);
	return black_contrast < white_contrast ? 'black' : 'white';
};
