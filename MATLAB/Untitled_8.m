img = imread("Pics/pic_7.jpg");
%figure
imshow(img)

hI=rgb2hsv(img);
%figure
%imshow(hI)
hImage1=hI(:,:,1);
sImage1=hI(:,:,2);
vImage1=hI(:,:,3);

%imshow(hI)
d=impixel(hI);