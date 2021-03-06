#coding:utf-8
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required

#对应文章的评论
@api.route('/post/<int:id>/comments/')
def get_post_comment(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page',1,type = int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).pagination(
        page,per_page = current_app.config['SHARING_COMMENT_PER_PAGE'],
        error_out = False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1, _external=True)
    return jsonify({
        'comments':[comment.to_json() for comment in comments],
        'prev':prev,      #prev变量储存了一个URL例如：/post/1/comments/
        'next':next,      #next变量储存了一个URL例如：/post/3/comments/
        'count':pagination.total
        })

#撰写评论
@api.route('/post/<int:id>/comments/',methods = ['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post 
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()),201, \
    {'Location':url_for('api.get_comment',id = comment.id,_external =True)}
