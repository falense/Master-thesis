function make_triangulation( x1,y1,x2,y2,x3,y3,xe,ye )
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

figure();
axis ([0 100 0 100]);
grid on
hold on

xlabel('Position X');
ylabel('Position Y');
title('Triangulation');

%plotLine(10,20,0,50);
a = (ye-y1)/(xe-x1)
if (xe > x1)
    plotLine(x1,y1,100,y1+a*(100-x1));
else
    plotLine(x1,y1,0,-a*100);
end
a = (y2-ye)/(x2-xe)
if (xe > x2)
    plotLine(x2,y2,100,y2+a*(100-x2));
else
    plotLine(x2,y2,0,-a*x2+y2);
end
a = (y3-ye)/(x3-xe)
if (xe > x3)
    plotLine(x3,y3,100,y3+a*(100-x3));
else
    plotLine(x3,y3,0,-a*x3+y3);
end
plotEmitter(xe,ye);


hold off

end

