
figure();
axis ([0 100 0 100]);
grid on
hold on

xlabel('Position X');
ylabel('Position Y');
title('Triangulation');

%plotLine(10,20,0,50);
plotLine(50,90,30,0);
plotLine(80,20,0,80);
plotEmitter(41,49);


hold off