function make_multilateration( x1,y1,x2,y2,x3,y3,xe,ye )

figure();
axis ([0 100 0 100]);
grid on
hold on

xlabel('Position X');
ylabel('Position Y');
title('Multilateration');

%plotLine(10,20,0,50);
d1 = distance(x1,y1,xe,ye)
d2 = distance(x2,y2,xe,ye)
d3 = distance(x3,y3,xe,ye)

plotReceivers(x1,y1,x2,y2,round(abs(d1-d2)))
plotReceivers(x1,y1,x3,y3,round(abs(d1-d3)))
plotReceivers(x2,y2,x3,y3,round(abs(d2-d3)))

plotEmitter(xe,ye)

hold off
end

