img=imread("Pics/red_obj.jpg");
%figure
%imshow(img);

hI=rgb2hsv(img);
figure
imshow(hI);
hImage1=hI(:,:,1);
sImage1=hI(:,:,2);
vImage1=hI(:,:,3);
d=impixel(hI);