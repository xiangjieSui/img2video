function [ fin_score ] = Temporal_Hysteresis( score_pre, K)
%---------Temporal Hysteresis--------%
% [Input]: 
%  (1) score_pre: Quality scores of video sequence;
%  (2) K : The frame number related to duration of memory (2 seconds).
% [Output]:
%  (1) fin_score: The final quality score of video sequence.
%------------------------------------%

[~,len] = size(score_pre);
alpha = 0.8;

for i = 1:len
    t_min = max(1,i-K);
    t_max = min(i+K,len);
    % memory component
    if i == 1
       memory_score  = score_pre(1);
    else
       memory_score = min(score_pre(t_min : i-1));
    end
    
    % current component
    reorder = sort(score_pre(i : t_max));
    [~,L] = size(reorder);
    sigma = (2*L-1)/12;
    gausFilter = fspecial('gaussian', [1,2*L], sigma);
    half_gausFilter = 2 * gausFilter(L+1:end);
    curr_score = sum(reorder.*half_gausFilter)/sum(half_gausFilter);
    
    % linear combining
    score_index(i) = alpha*curr_score+(1-alpha)*memory_score;
end

fin_score = nanmean(score_index);

end

