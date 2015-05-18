function plotReceivers(x1,y1,x2,y2,a)
    for x=1:100,
        for y=1:100,
            t = distance(x,y,x1,y1);
            t2 = distance(x,y,x2,y2);
            s = (t-t2)^2;
            if s < (a+1)^2  && s > (a-1)^2
                scatter(x,y,3,[0.5 0.5 0.8])
            end
        end
    end
    
    plot(x1,y1,'x',...
    'LineWidth',2,...
            'MarkerSize',15);

    plot(x2,y2,'x',...
    'LineWidth',2,...
            'MarkerSize',15);
end

