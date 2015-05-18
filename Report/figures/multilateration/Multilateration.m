
figure();
axis ([0 100 0 100]);
grid on
hold on

xlabel('Position X');
ylabel('Position Y');
title('Multilateration');

%plotLine(10,20,0,50);
plotReceivers(30,50,70,50,20)
plotReceivers(40,80,70,50,10)
plotReceivers(30,50,40,80,30)

plotEmitter(33,25)

hold off