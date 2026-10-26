---
name: blog.smarter.sh-publish
description: Use when asked to publish, upload, post, update or draft a post on blog.smarter.sh (WordPress) yourself, e.g. "publish the release announcements to the blog", "post this to the WordPress blog", "fix the typo in the v0.21 post", or when asked which release announcement was published last. Covers the credentials in .env, why the scripts log in with a cookie and REST nonce instead of Application Passwords, converting a Markdown post to the Gutenberg blocks the blog uses (md2wp.py), wp.py's whoami/list/get/publish/upload commands, adding screenshots and images, titles, slugs and categories, the draft-check-publish routine, verifying the public page, and choosing which releases to group into one announcement.
---

# Publishing to blog.smarter.sh

[blog.smarter.sh](https://blog.smarter.sh) is a WordPress site. You can read and
publish its posts yourself through the WordPress REST API, with the two scripts
in [scripts/](scripts/). Write the post first, with
`blog.smarter.sh-release-announcement` or `blog.smarter.sh-blog-post`. This
skill only takes a finished Markdown file to a published post.

It's a copy of the skill of the same name in
[Smarter's skills](https://github.com/smarter-sh/smarter/tree/main/skills/blog.smarter.sh-publish),
with the same scripts, so that this repository can publish its own release
announcements. When you fix something here, fix it there too.

Publishing is public. A post can be cached, indexed and syndicated before you
take it down. Publish only when the user has asked you to publish. Otherwise
upload a draft and give them the draft's id.

## Credentials

The scripts read `WP_URL`, `WP_USERNAME` and `WP_PASSWORD` from the environment,
or, when they are not set there, from this repository's git-ignored `.env`, and
then from the `.env` of the [smarter](https://github.com/smarter-sh/smarter)
checkout beside this one (`../smarter/.env`), where the user keeps them. So a
fresh shell usually has none of them set, and that is fine. Don't copy them into
this repository's `.env`: one copy is easier to keep secret and to rotate.
`WP_URL` is the login page (`https://blog.smarter.sh/wp-login.php`). The scripts
use only its scheme and host.

- Never print, echo or log the password, and never copy it into a file, a
  command line or the conversation. To check that it's set, print its length.
- The account is an administrator. Don't change users, plugins, settings or
  other people's posts.

## Why cookie login, not Application Passwords

The REST index (`https://blog.smarter.sh/wp-json/`) lists no authentication
methods. Wordfence turns Application Passwords off, so HTTP Basic auth with
the login password answers `rest_not_logged_in`. `wp.py` logs in the way a
browser does instead:

1. GET `wp-login.php`, which sets the test cookie.
2. POST `log`, `pwd`, `testcookie=1` and `redirect_to=/wp-admin/` to
   `wp-login.php`. A 302 to `/wp-admin/` means success.
3. GET `/wp-admin/admin-ajax.php?action=rest-nonce`, which returns a
   10-character nonce (or `0` when the login failed).
4. Send the session cookies and an `X-WP-Nonce` header on every REST request.

If Wordfence ever adds a CAPTCHA or two-factor login, step 2 will fail.
`wp.py` stops with "login failed". Tell the user. Don't try to get around it.

## How the posts are stored

The posts are Gutenberg block markup, not Markdown or classic HTML:
`wp:heading`, `wp:paragraph`, `wp:list`/`wp:list-item`, `wp:table`,
`wp:quote`, `wp:separator`, and the SyntaxHighlighter plugin's
`wp:syntaxhighlighter/code` for code. [scripts/md2wp.py](scripts/md2wp.py)
converts the Markdown that the release announcements use into exactly those
blocks. Run on `blog.smarter.sh-release-announcement/references/example-v0.16.md`,
it gives the same blocks as the published v0.16 post. So a converted post
opens cleanly in the block editor, and the user can edit it there.

- Supported: ATX headings, paragraphs, one level of `-` or `1.` lists (an
  indented line continues the item), pipe tables, `>` quotes, `---`, fenced
  code, and inline `**bold**`, `*italics*`, `` `code` `` and `[links](url)`.
  An image is `![alt](url "caption")` on a line of its own, and becomes an
  image block linked to the full-size file. Nested lists, inline images and
  raw HTML are not supported. Keep the post within that.
- Code fences need a language that SyntaxHighlighter has a brush for: `bash`,
  `yaml`, `python`, `jscript`, `sql`, `xml`, `css`, `diff` or `plain`. An
  unknown language, such as `typescript` or `toml`, renders as unhighlighted
  text with curly quotes. md2wp maps `ts`, `typescript`, `js` and `json` to
  `jscript`, `console`, `sh` and `zsh` to `bash`, and `toml`, `ini`, `text`
  and a fence with no language to `plain`. To check that a brush exists, look
  for a 200 from
  `https://blog.smarter.sh/wp-content/plugins/syntaxhighlighter/syntaxhighlighter3/scripts/shBrush<Name>.js`,
  then add it to the map.
- **The H1 and the date line are not part of the content.** The theme prints
  the WordPress title and the publication date above every post, so md2wp drops
  the Markdown's first `# ...` line and the `Month D, YYYY · The Smarter
Project` line after it. Left in, they showed every post's title and date
  twice, and the user had them removed from every published post. `publish`
  uses the H1 as the WordPress title unless you pass `--title`. A date line
  with an update note (`October 21, 2026, updated October 25 for v0.36.20 ·
The Smarter Project`) keeps the note as an italic first paragraph. Never add
  a title, H1 or date to a post's content by hand.

## The commands

```bash
S=skills/blog.smarter.sh-publish/scripts
$S/wp.py whoami                    # {"id": 1, "name": "smarter_blog", "roles": ["administrator"]}
$S/wp.py categories                # 4 announcements Announcements ...
$S/wp.py list --status any         # id, date, status, slug, categories, title
$S/wp.py get 132 --raw /tmp/x.html # a post's metadata, and its block markup
$S/wp.py publish ~/desktop/blog-v0.21-v0.23.md \
  --slug release-v0-21-v0-23 --category 4 --status draft
$S/wp.py publish ... --status publish --id 319   # update post 319, here to publish it
$S/wp.py upload ~/desktop/shot.png --alt "What the image shows"  # id and source_url
```

To add a screenshot, `upload` it and put its `source_url` in an image line.
Resize it to 1680 px wide first (`sips --resampleWidth 1680 in.png --out
<scratchpad>/out.png`). A larger image, such as a 3000 px Retina screenshot,
makes WordPress answer 500 while it builds the resized copies. The file is
saved anyway, but without its large sizes and never moved to
`cdn.blog.smarter.sh`. If that happens, delete the broken media item
(`DELETE media/<id>` with `force=true`) and upload the resized file. Read an
image before uploading it. It is public too, so check it shows no keys,
hostnames, account numbers or customer data.

### Featured images

Every article needs a featured image. The theme shows it on the post and on the
home page's post cards. Release announcements (category 4) have none. Recent
articles use flat, colorful vector illustrations on a white background (people,
robots, browser windows, clouds, in orange, yellow, teal, navy and blue), or a
close-up photo of code, at 1680 px wide and roughly 3:2.

**The Smarter Project has an Envato account**, so licensed stock illustrations
and photos from Envato are the first choice for a featured image. You can't
sign in to Envato or license an item yourself. Suggest two or three search
terms, or Envato items that suit the post, and ask the user to download the
one they pick. Then resize it to 1680 px wide, `upload` it with alt text that
says what it shows, and set it on the post:

```bash
python3 -c '
from wp import Blog
b = Blog()
p = b.request("GET", "posts/<id>", context="edit")
# send the content too, so Yoast SEO rebuilds the post's og:image
b.request("POST", "posts/<id>", {"featured_media": <media id>, "content": p["content"]["raw"]})
print(b.request("GET", "posts/<id>", context="edit")["yoast_head_json"]["og_image"][0]["url"])
'
```

Setting `featured_media` alone changes the image on the page but not Yoast
SEO's `og:image`, which link previews in Slack, LinkedIn and the like use: it
keeps the old image, or none. Saving the content in the same request makes Yoast
rebuild it. The command prints the new `og:image` url. Check that it is the new
file, then clear the page cache.

An original illustration that you draw is also fine, when no Envato item fits
or the user would rather not pick one. The featured image of "Getting Started
With smarter-api" (media 437) was made this way, and the user approved it.
Draw an SVG in the same flat style and palette, about the post's own subject,
render it with `rsvg-convert -w 1680 -h 1120`, and read the PNG before
uploading it. Put `xml:space="preserve"` on any text group with
code, or rsvg drops the spaces between words. Don't use trademarked logos,
such as Python's. Before reusing an image from the media library, check that
no other post uses it as its featured image.

`publish` without `--id` creates a new post every time. To change a post, pass
its `--id`, or you'll publish a duplicate. It closes comments, like the earlier
posts.

**Never create a second post for an article that already exists**, not even a
draft "for review". Two posts with one title in wp-admin confuse the user, who
can't tell which one is live. An agent once copied a published post into a
"REVISION of post 376" draft for review, then published the edits to the
original and left the draft behind. The user had it deleted and said never to
do that again. To change an existing post, edit that post by its `--id`. If the
user wants to review edits before they go live, show the changed passages in
the conversation and update the post once they approve.

## Conventions

| Field     | Release announcement                                                       | Example                                                                |
| --------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Title     | the Markdown's H1, `smarter-types vX.Y Release: <theme>`, or `vX.Y – vX.Z` | `cache-results v0.1 Release: Smarter's Caching Decorator, Now on PyPI` |
| Slug      | `release-smarter-types-vX-Y`, or `release-smarter-types-vX-Y-vX-Z`         | `release-cache-results-v0-1`                                           |
| Category  | 4, Announcements                                                           |                                                                        |
| Date line | in the Markdown only, the day you publish                                  | `October 25, 2026 · The Smarter Project`                               |

An article's title is its H1 too. Use the en dash (–) in a version range.

Other articles use category 6 (Artificial Intelligence), 5 (How To) or 9
(System Management). Run `categories` for the current list. The home page
leaves out category 4 (a Code Snippets snippet, "Home page: hide
Announcements", in wp-admin > Snippets). Announcements are listed in the Main
Sidebar's "Announcements" widget instead. So put release announcements and other
administrative posts in category 4, and never add 4 to an article. Leave the
publication date to WordPress (now), and keep the Markdown source at
`~/desktop/blog-<slug>.md`.

Post cards show no excerpt. That is snippet 6, "Post cards: hide excerpts", a
front-end PHP snippet that prints `.entry-card .entry-excerpt { display: none; }`
in `wp_head`. Its CSS goes through PHP because the blog does not serve Code
Snippets' `site-css` snippets. The Code Snippets REST API
(`/wp-json/code-snippets/v1/snippets`) accepts the same login and nonce as
`wp.py`.

Every article ends with the author's signature: "Lawrence McDaniel – Author,
The Smarter Project", with the name linked to lawrencemcdaniel.com, and a
one-line bio under it. Announcements (category 4) don't.
That is snippet 7, "Posts: author signature", a `the_content` filter plus its
CSS in `wp_head`. So don't write a signature or bio into a post's Markdown: it
would appear twice.

WP Super Cache serves pages to visitors, and saving a snippet or theme setting
does not clear it. After such a change, delete the whole cache: read the
`wpsc_ajax` nonce from `wp-admin/options-general.php?page=wpsupercache`, then
POST `action=ajax-delete-cache&path=/&admin=1&nonce=<nonce>` to
`wp-admin/admin-ajax.php`. Verify with the plain url, not a `?query` url,
which bypasses the cache and shows you a page that visitors don't get.

## Routine

1. **Find what to announce, and write the post** with
   `blog.smarter.sh-release-announcement`, which finds the last announced
   release with `wp.py list --search "smarter-types"`.
2. **Upload a draft**, then check the rendered HTML, which `wp.py` can read
   while the post is a draft:

   ```bash
   cd skills/blog.smarter.sh-publish/scripts && python3 -c '
   import re
   from wp import Blog
   r = Blog().request("GET", "posts/<id>", context="edit")["content"]["rendered"]
   print(re.findall(r"<pre class=\"brush: \w+", r))   # one per code fence
   text = re.sub(r"<[^>]+>", "", re.sub(r"<pre.*?</pre>", "", r, flags=re.S))
   print(re.findall(r"\*\*|`|\]\(", text))           # leftover Markdown: should be []
   '
   ```

   Every code fence must appear as a `brush:`. A code block that renders as a
   plain `<div>` has an unknown language.

3. **Publish** with `--status publish --id <id>`, if the user asked you to.
4. **Verify the public page.** `curl -sL -o /dev/null -w '%{http_code}' <link>`
   gives 200, and the page's `<title>` is the post's title.
5. **Report** the post's link, which releases it covers, and the claims to
   review (see the release announcement skill's last section).

## Pitfalls

- The host shell is zsh. `${(P)name}` reads a variable by name, and an unquoted
  `--include=*.py` is a glob error. Pass arguments to the scripts quoted.
- `.env` is git-ignored. Make sure it stays that way (`git check-ignore .env`),
  and never add the credentials to a skill, a script or a commit.
- A post on the blog is not the source. If the user edits a post in WordPress
  and you republish the Markdown with `--id`, their edit is lost. First compare
  with `wp.py get <id> --raw`.
