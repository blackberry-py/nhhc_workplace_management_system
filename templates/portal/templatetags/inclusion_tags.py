from django import template


register = template.Library()

# @register.inclusion_tag(filename="blog/post-list.html")
# def recent_announcements() -> dict[str, Union[str, QuerySet[Post]]]:
#     """Includes a list of most recent posts in blog/post-list.html."""
#     posts = Post.objects.exclude(pk=post.id).order_by("-created_at").filter(status="P")[:5]
#     return {"title": "Recent Posts", "posts": posts}
