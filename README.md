# OMR Sheet Auto Grader using template matching and non maximal supression.
	Instructions for running the code:
	There are three files: grade.py, inject.py and extract.py.
	The file: basic_template.txt has to be in the same folder as grade.py for it to run.
	The input images should be in jpg format.
	The program  accepts a scanned image file of a printed form, and produces
	an output fille that contains the student's marked answers. The program runs like this:
	./grade.py form.jpg output.jpg output.txt.
	output.txt xontains the marked answers.
# Assumptions:
	Grayscale input image was binarized with a threshold of 127.
	The image boxes will be parallel to each other with respect to both the axis.
	The relative distance between any two boxes will be roughly same.
	The horizontal distance between the boxes was assumed to be 40 pixels and the verticaldistance was assumed to be 35 pixels.
	A box was selected as answer if the average intensity within that box is less than .65
	The detected bubbled marks by the student were shaded with grayish white pixels of intensity 200 in the output jpgs.
	To detect any input characters to the left of a question, a range of intensities were calculated and checked if the minimum 		among them is less than .9 (As, most of the part will be white). The bar code for the inject-extract module is placed with two 		circular marks on it’s either side. The scanned image is assumed to contain the barcode within those marks.
# Design Decisions and Methodology:
# Template Matching:
	A basic template was constructed from bank form, where almost all the boxes were of even
	shape and this information was used in detecting boxes in the test samples
	Template matching was carried out by comparing the edge of template to that of selected
	portion of the image. As, this will ensure there will be high similarity between template and
	boxes as both have same edge structure (square boundaries)
	We have selected all possible horizontal and vertical lines (with the help of coordinates of
	the template matching) if the similarity with template edges is greater than 70%
	Once all the possible horizontal and vertical lines are compiled, a threshold of minimum 8
	and 12 occurrences were used to select most favourable horizontal and vertical lines as per
	image. As, there are more boxes in the vertical direction a relatively high threshold was
	used.
	Using these lines in sorted order (from top to bottom for horizon lines and from left to right
	for vertical lines), possible missing horizontal lines were imputed (As we know there has to
	a horizontal line in every 50~60-pixel distance).
	Finally, a list of horizontal and vertical coordinates was computed using lines and this will
	give us all coordinates of all the questions present in the sheet
	Once boxes were found, we have found the average box intensity and there by determined
	whether it was marked by student or not.
	Similarly, average intensity to the left of each question was calculated to check for presence
	of characters.
	Finally, saved the required image and text file
	The image templates are arrays that have been manually subsetted from the image for each
	letter choice.
# Barcode detection:
	Barcodes were generated using three random unique numbers between 0 and 9 which
	represent the width of each block in the barcode.
	The barcode was imposed at the bottom of the image along with two black circles at either
	of its scan-line corners.
	These three digit codes were used as keys in a dictionary mapping to the answer key and
	were written out as a JSON object.
	When a scanned image is read, the two black circular artifacts are detected using template
	matching and a line is drawn with the two circles as the end points.
	This line is used correct the alignment of the image.
	The scan-line segment of the barcode of length 1000 pixels with 10 pixels up and down is
	taken to get a subarray. The three digit barcode code is detected using the mean of the blocks
	and their ratios.
