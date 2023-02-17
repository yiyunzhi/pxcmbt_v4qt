# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_reimpl_biastar.py
# ------------------------------------------------------------------------------
#
# File          : _test_reimpl_biastar.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from application.module.pathplanner.bi_dir_astar import get_theta_angle, get_direction_change, PointLike, BidirectionalAStar, GridMap, render_path


def cost_modifier(p_from, p_to, algo: BidirectionalAStar):
    """
    p_from is start from goal point
    p_from: from
    p_to: to
    algo: instance of algorithm
    """
    # if algo.distance <= GRID:
    #     return 0
    _ds = 1 if p_from == algo.sStart else algo.h2(algo.sStart, p_to)
    _de = 1 if p_to == algo.sGoal else algo.h2(algo.sGoal, p_to)
    _ds = 1 if _ds == 0 else _ds
    _de = 1 if _de == 0 else _de
    # _angle = get_theta_angle(PointLike(*p_from), PointLike(*p_to))
    if p_from == algo.sStart:
        _previous_angle = start_angle
        _dir = 'F'
    elif p_from == algo.sGoal:
        _previous_angle = goal_angle
        _dir = 'B'
    else:
        if p_from in algo.parentFore:
            _parent_p = algo.parentFore[p_from]
            _dir = 'F'
        else:
            _parent_p = algo.parentBack[p_from]
            _dir = 'B'
        _previous_angle = get_theta_angle(PointLike(*_parent_p), PointLike(*p_from))
    _move_angle = get_theta_angle(PointLike(*p_from), PointLike(*p_to))
    if _dir == 'F':
        _d = _ds
        _angle_change = get_direction_change(start_angle, _move_angle)
        _cost = START_CHANGE_ANGLE_COST[_angle_change] + algo.h(p_from, p_to)
    else:
        _d = _de
        _angle_change = get_direction_change(goal_angle, _move_angle)
        _cost = END_CHANGE_ANGLE_COST[_angle_change] + algo.h(p_from, p_to)

    print('DIR:{} MoveAngle:{}\tCost:{},\tFrom:{},To:{}'.format(_dir, _move_angle, _cost, p_from, p_to))
    return _cost


def f_value_fore_modifier(s, algo: BidirectionalAStar):
    if s==algo.sStart:
        return 0
    _parent_p = algo.parentFore[s]
    if _parent_p == algo.sStart:
        _previous_angle = start_angle
        _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
    else:
        _grand_parent_p = algo.parentFore[_parent_p]
        _previous_angle = get_theta_angle(PointLike(*_grand_parent_p), PointLike(*_parent_p))
        _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
    _d=algo.h3(s,(int((algo.sStart[0]+algo.sGoal[0])/2),int((algo.sStart[1]+algo.sGoal[1])/2)))
    return get_direction_change(_angle, _previous_angle)+_d


def f_value_back_modifier(s, algo: BidirectionalAStar):
    if s==algo.sGoal:
        return 0
    _parent_p = algo.parentBack[s]
    if _parent_p == algo.sGoal:
        _previous_angle = goal_angle
        _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
    else:
        _grand_parent_p = algo.parentBack[_parent_p]
        _previous_angle = get_theta_angle(PointLike(*_grand_parent_p), PointLike(*_parent_p))
        _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
    _d=algo.h3(s,(int((algo.sStart[0]+algo.sGoal[0])/2),int((algo.sStart[1]+algo.sGoal[1])/2)))
    return get_direction_change(_angle, _previous_angle)+_d


GRID_X = 20
GRID_Y = 10
x_start = (0, 0)
x_goal = (19, 9)
_gmap = GridMap(GRID_X, GRID_Y)
bastar = BidirectionalAStar(x_start, x_goal, _gmap)
bastar.fValueForeModifier = f_value_fore_modifier
bastar.fValueBackModifier = f_value_back_modifier
# bastar.costModifier = cost_modifier
start_angle = 180
goal_angle = 180
START_CHANGE_ANGLE_COST = {90.0: 50, 180.0: 50, 0.0: 1, 270.0: 50}
END_CHANGE_ANGLE_COST = {90.0: 50, 180.0: 50, 0.0: 1, 270.0: 50}


def main():
    # x_start = (45, 11)
    # x_goal = (2, 3)
    _t = time.time()
    # _gmap.add_obstacles([(10, 9), (10, 10), (10, 11), (10, 12)])

    # plot = Plotting(x_start, x_goal)

    path, visited_fore, visited_back = bastar.search()
    print('time usage:', time.time() - _t)
    print('pathLength:%s, visited_fore: %s,visited_back: %s' % (len(path), len(visited_fore), len(visited_back)))
    render_path(_gmap, path, visited_fore, visited_back)
    # plot.animation_bi_astar(path, visited_fore, visited_back, "Bidirectional-A*")  # animation


if __name__ == '__main__':
    import time

    main()
