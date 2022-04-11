import * as markdown from "markdown-it";
import * as colors from "markdown-it-colors";
import hljs from "highlight.js";

import "highlight.js/styles/monokai-sublime.css";
console.log(hljs);

const Readme = ({ text = "" }) => {
  var md = markdown({
    gfm: true,
    pedantic: false,
    sanitize: false,
    tables: true,
    breaks: false,
    smartLists: true,
    smartypants: false,
    highlight: function (code) {
      return hljs.highlightAuto(code).value;
    },
  });

  console.log(md);
  console.log(markdown());
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: md.render(text),
      }}
    ></div>
  );
};

export default Readme;
