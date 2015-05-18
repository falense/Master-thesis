function make_trilateration( x1,y1,x2,y2,x3,y3,xe,ye )
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
figure();
axis ([0 100 0 100]);
grid on
hold on

xlabel('Position X');
ylabel('Position Y');
title('Trilateration');

plotReceiver(x1,y1,distance(x1,y1,xe,ye))
plotReceiver(x2,y2,distance(x2,y2,xe,ye))
plotReceiver(x3,y3,distance(x3,y3,xe,ye))

plotEmitter(xe,ye)

hold off

end

