function plotCircle(x,y,r)
theta = 0 : 0.01 : 2*pi;
x = r * cos(theta) + x;
y = r * sin(theta) + y;
plot(x, y,'LineWidth',1);
end