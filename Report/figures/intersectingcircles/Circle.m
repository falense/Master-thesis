
figure();
axis equal
grid on
hold on

xlabel('Position X');
ylabel('Position Y');
title('Naive geolocation algorithm');

plotReceiver(50,30,20)
plotReceiver(25,60,30)
plotReceiver(76,60,25)
plotEmitter(53.26,49.61)
hold off