/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

export const invertColor = (hexTripletColor: string): string => {
	let color = hexTripletColor;
	color = color.substring(1); // remove #
	let color_int = parseInt(color, 16); // convert to integer
	color_int = 0xffffff ^ color_int; // invert three bytes
	color = color_int.toString(16); // convert to hex
	color = ('000000' + color).slice(-6); // pad with leading zeros
	color = '#' + color; // prepend #
	return color;
};

export const calculate_score = (q_time: number, time_taken: number): number => {
	return q_time / time_taken;
};
