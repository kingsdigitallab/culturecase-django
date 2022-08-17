// Mobile Menu (GN)
jQuery(function($) {
    $('.kdl-mobile-menu .dd-select').on('click', function() {
        $(this).parent().toggleClass('kdl-mobile-menu-open');
    });
});


// head
WebFontConfig = {
    google: { families: [ "PT+Sans:400,400italic,700,700italic:latin,greek-ext,cyrillic,latin-ext,greek,cyrillic-ext,vietnamese", "Sorts+Mill+Goudy:400,400italic,700,700italic:latin,greek-ext,cyrillic,latin-ext,greek,cyrillic-ext,vietnamese" ] },      custom: { families: ['FontAwesome'], urls: ['/static/www.culturecase.org/wp-content/themes/Avada/fonts/fontawesome.css'] }
};
(function() {
    var wf = document.createElement('script');
    wf.src = ('https:' == document.location.protocol ? 'https' : 'http') +
      '://ajax.googleapis.com/ajax/libs/webfont/1/webfont.js';
    wf.type = 'text/javascript';
    wf.async = 'true';
    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(wf, s);
})();

// ------------------------------

// GN: removed emoji, calls missing file over http => errors
// window._wpemojiSettings = {"baseUrl":"http:\/\/s.w.org\/images\/core\/emoji\/72x72\/","ext":".png","source":{"concatemoji":"http:\/\/www.culturecase.org\/wp-includes\/js\/wp-emoji-release.min.js?ver=4.3"}};
// !function(a,b,c){function d(a){var c=b.createElement("canvas"),d=c.getContext&&c.getContext("2d");return d&&d.fillText?(d.textBaseline="top",d.font="600 32px Arial","flag"===a?(d.fillText(String.fromCharCode(55356,56812,55356,56807),0,0),c.toDataURL().length>3e3):(d.fillText(String.fromCharCode(55357,56835),0,0),0!==d.getImageData(16,16,1,1).data[0])):!1}function e(a){var c=b.createElement("script");c.src=a,c.type="text/javascript",b.getElementsByTagName("head")[0].appendChild(c)}var f,g;c.supports={simple:d("simple"),flag:d("flag")},c.DOMReady=!1,c.readyCallback=function(){c.DOMReady=!0},c.supports.simple&&c.supports.flag||(g=function(){c.readyCallback()},b.addEventListener?(b.addEventListener("DOMContentLoaded",g,!1),a.addEventListener("load",g,!1)):(a.attachEvent("onload",g),b.attachEvent("onreadystatechange",function(){"complete"===b.readyState&&c.readyCallback()})),f=c.source||{},f.concatemoji?e(f.concatemoji):f.wpemoji&&f.twemoji&&(e(f.twemoji),e(f.wpemoji)))}(window,document,window._wpemojiSettings);

//------------------------------

(function() {
    if (!window.mc4wp) {
        window.mc4wp = {
            listeners: [],
            forms    : {
                on: function (event, callback) {
                    window.mc4wp.listeners.push({
                        event   : event,
                        callback: callback
                    });
                }
            }
        }
    }
})();

// -----------------------------

/*@cc_on
@if (@_jscript_version == 10)
  document.write('<style type="text/css">.search input{padding-left:5px;}header .tagline{margin-top:3px !important;}</style>');
@end
@*/
function insertParam(url, parameterName, parameterValue, atStart){
  replaceDuplicates = true;
  if(url.indexOf('#') > 0){
      var cl = url.indexOf('#');
      urlhash = url.substring(url.indexOf('#'),url.length);
  } else {
      urlhash = '';
      cl = url.length;
  }
  sourceUrl = url.substring(0,cl);

  var urlParts = sourceUrl.split("?");
  var newQueryString = "";

  if (urlParts.length > 1)
  {
      var parameters = urlParts[1].split("&");
      for (var i=0; (i < parameters.length); i++)
      {
          var parameterParts = parameters[i].split("=");
          if (!(replaceDuplicates && parameterParts[0] == parameterName))
          {
              if (newQueryString == "") {
                  newQueryString = "?";
              }
              else {
                  newQueryString += "&";
              newQueryString += parameterParts[0] + "=" + (parameterParts[1]?parameterParts[1]:'');
              }
          }
      }
  }
  if (newQueryString == "")
      newQueryString = "?";

  if(atStart){
      newQueryString = '?'+ parameterName + "=" + parameterValue + (newQueryString.length>1?'&'+newQueryString.substring(1):'');
  } else {
      if (newQueryString !== "" && newQueryString != '?')
          newQueryString += "&";
      newQueryString += parameterName + "=" + (parameterValue?parameterValue:'');
  }
  return urlParts[0] + newQueryString + urlhash;
};

function ytVidId(url) {
var p = /^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
return (url.match(p)) ? RegExp.$1 : false;
//return (url.match(p)) ? true : false;
}

jQuery(document).ready(function() {
  jQuery('.portfolio-wrapper').hide();
});
jQuery(window).load(function() {
  if(jQuery('#sidebar').is(':visible')) {
      jQuery('.post-content div.portfolio').each(function() {
          var columns = jQuery(this).data('columns');
          jQuery(this).addClass('portfolio-'+columns+'-sidebar');
      });
  }
  jQuery('.full-video, .video-shortcode, .wooslider .slide-content').fitVids();

  if(jQuery().isotope) {
        // modified Isotope methods for gutters in masonry
        jQuery.Isotope.prototype._getMasonryGutterColumns = function() {
          var gutter = this.options.masonry && this.options.masonry.gutterWidth || 0;
              containerWidth = this.element.width();

          this.masonry.columnWidth = this.options.masonry && this.options.masonry.columnWidth ||
                        // or use the size of the first item
                        this.$filteredAtoms.outerWidth(true) ||
                        // if there's no items, use size of container
                        containerWidth;

          this.masonry.columnWidth += gutter;

          this.masonry.cols = Math.floor( ( containerWidth + gutter ) / this.masonry.columnWidth );
          this.masonry.cols = Math.max( this.masonry.cols, 1 );
        };

        jQuery.Isotope.prototype._masonryReset = function() {
          // layout-specific props
          this.masonry = {};
          // FIXME shouldn't have to call this again
          this._getMasonryGutterColumns();
          var i = this.masonry.cols;
          this.masonry.colYs = [];
          while (i--) {
            this.masonry.colYs.push( 0 );
          }
        };

        jQuery.Isotope.prototype._masonryResizeChanged = function() {
          var prevSegments = this.masonry.cols;
          // update cols/rows
          this._getMasonryGutterColumns();
          // return if updated cols/rows is not equal to previous
          return ( this.masonry.cols !== prevSegments );
        };

      imagesLoaded(jQuery('.portfolio-one .portfolio-wrapper'), function() {
          jQuery('.portfolio-wrapper').fadeIn();
          jQuery('.portfolio-one .portfolio-wrapper').isotope({
              // options
              itemSelector: '.portfolio-item',
              layoutMode: 'straightDown',
              transformsEnabled: false
          });
      });

      imagesLoaded(jQuery('.portfolio-two .portfolio-wrapper, .portfolio-three .portfolio-wrapper, .portfolio-four .portfolio-wrapper'),function() {
          jQuery('.portfolio-wrapper').fadeIn();
          jQuery('.portfolio-two .portfolio-wrapper, .portfolio-three .portfolio-wrapper, .portfolio-four .portfolio-wrapper').isotope({
              // options
              itemSelector: '.portfolio-item',
              layoutMode: 'fitRows',
              transformsEnabled: false
          });
      });

      var masonryContainer = jQuery('.portfolio-masonry .portfolio-wrapper');
      imagesLoaded(masonryContainer, function() {
          jQuery('.portfolio-wrapper').fadeIn();
          var gridTwo = masonryContainer.parent().hasClass('portfolio-grid-2');
          var columns;
          if(gridTwo) {
              columns = 2;
          } else {
              columns = 3;
          }
          masonryContainer.isotope({
              // options
              itemSelector: '.portfolio-item',
              layoutMode: 'masonry',
              transformsEnabled: false,
              masonry: { columnWidth: masonryContainer.width() / columns }
          });
      });
  }

  if(jQuery().flexslider) {
      var WooThumbWidth = 100;
      if(jQuery('body.woocommerce #sidebar').is(':visible')) {
          wooThumbWidth = 100;
      } else {
          wooThumbWidth = 118;
      }

      jQuery('.woocommerce .images #carousel').flexslider({
          animation: 'slide',
          controlNav: false,
          directionNav: false,
          animationLoop: false,
          slideshow: false,
          itemWidth: wooThumbWidth,
          itemMargin: 9,
          touch: false,
          useCSS: false,
          asNavFor: '.woocommerce .images #slider'
      });

      jQuery('.woocommerce .images #slider').flexslider({
          animation: 'slide',
          controlNav: false,
          animationLoop: false,
          slideshow: false,
          smoothHeight: true,
          touch: true,
          useCSS: false,
          sync: '.woocommerce .images #carousel'
      });

      var iframes = jQuery('iframe');
      var avada_ytplayer;

      jQuery.each(iframes, function(i, v) {
          var src = jQuery(this).attr('src');
          if(src) {
                                  if(src.indexOf('vimeo') >= 1) {
                  jQuery(this).attr('id', 'player_'+(i+1));
                  var new_src = insertParam(src, 'api', '1', false);
                  var new_src_2 = insertParam(new_src, 'player_id', 'player_'+(i+1), false);

                  jQuery(this).attr('src', new_src_2);
              }
                                                      if(ytVidId(src)) {
                  jQuery(this).parent().wrap('<span class="play3" />');
                  window.yt_vid_exists = true;
              }
                              }
      });

      if(window.yt_vid_exists == true) {
          var tag = document.createElement('script');
          tag.src = "https://www.youtube.com/iframe_api";
          var firstScriptTag = document.getElementsByTagName('script')[0];
          firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

          function getFrameID(id){
              var elem = document.getElementById(id);
              if (elem) {
                  if(/^iframe$/i.test(elem.tagName)) return id; //Frame, OK
                  // else: Look for frame
                  var elems = elem.getElementsByTagName("iframe");
                  if (!elems.length) return null; //No iframe found, FAILURE
                  for (var i=0; i<elems.length; i++) {
                     if (/^https?:\/\/(?:www\.)?youtube(?:-nocookie)?\.com(\/|$)/i.test(elems[i].src)) break;
                  }
                  elem = elems[i]; //The only, or the best iFrame
                  if (elem.id) return elem.id; //Existing ID, return it
                  // else: Create a new ID
                  do { //Keep postfixing `-frame` until the ID is unique
                      id += "-frame";
                  } while (document.getElementById(id));
                  elem.id = id;
                  return id;
              }
              // If no element, return null.
              return null;
          }

          // Define YT_ready function.
          var YT_ready = (function() {
              var onReady_funcs = [], api_isReady = false;
              /* @param func function     Function to execute on ready
               * @param func Boolean      If true, all qeued functions are executed
               * @param b_before Boolean  If true, the func will added to the first
                                           position in the queue*/
              return function(func, b_before) {
                  if (func === true) {
                      api_isReady = true;
                      while (onReady_funcs.length) {
                          // Removes the first func from the array, and execute func
                          onReady_funcs.shift()();
                      }
                  } else if (typeof func == "function") {
                      if (api_isReady) func();
                      else onReady_funcs[b_before?"unshift":"push"](func);
                  }
              }
          })();
          // This function will be called when the API is fully loaded
          function onYouTubePlayerAPIReady() {YT_ready(true)}
      }
      
                  function ready(player_id) {
          var froogaloop = $f(player_id);

          froogaloop.addEvent('play', function(data) {
              jQuery('#'+player_id).parents('li').parent().parent().flexslider("pause");
          });

          froogaloop.addEvent('pause', function(data) {
              jQuery('#'+player_id).parents('li').parent().parent().flexslider("play");
          });
      }

      var vimeoPlayers = jQuery('.flexslider').find('iframe'), player;

      for (var i = 0, length = vimeoPlayers.length; i < length; i++) {
          player = vimeoPlayers[i];
          $f(player).addEvent('ready', ready);
      }

      function addEvent(element, eventName, callback) {
          if (element.addEventListener) {
              element.addEventListener(eventName, callback, false)
          } else {
              element.attachEvent(eventName, callback, false);
          }
      }
      
      jQuery('.tfs-slider').flexslider({
          animation: "fade",
          slideshow: true,
          slideshowSpeed: 7000,
          animationSpeed: 600,
          smoothHeight: true,
          pauseOnHover: false,
          useCSS: false,
          video: true,
          start: function(slider) {
              if(typeof(slider.slides) !== 'undefined' && slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                                                          YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          },
          before: function(slider) {
              if(slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                         $f( slider.slides.eq(slider.currentSlide).find('iframe').attr('id') ).api('pause');
                 
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                  
                 /* ------------------  YOUTUBE FOR AUTOSLIDER ------------------ */
                 playVideoAndPauseOthers(slider);
             }
          },
          after: function(slider) {
              if(slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                 
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          }
      });

                  jQuery('.grid-layout .flexslider').flexslider({
          slideshow: true,
          slideshowSpeed: 7000,
          video: true,
          smoothHeight: false,
          pauseOnHover: false,
          useCSS: false,
                          start: function(slider) {
              if (typeof(slider.slides) !== 'undefined' && slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                          jQuery(slider).find('.flex-control-nav').hide();
                  
                                          YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                      } else {
                                          jQuery(slider).find('.flex-control-nav').show();
                                      }
          },
          before: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                  $f(slider.slides.eq(slider.currentSlide).find('iframe').attr('id') ).api('pause');                                                YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                  
                  /* ------------------  YOUTUBE FOR AUTOSLIDER ------------------ */
                  playVideoAndPauseOthers(slider);
              }
          },
          after: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                          jQuery(slider).find('.flex-control-nav').hide();
                                                                  YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                      } else {
                                          jQuery(slider).find('.flex-control-nav').show();
                                      }
          }
      });
      jQuery('.flexslider').flexslider({
          slideshow: true,
          slideshowSpeed: 7000,
          video: true,
          smoothHeight: false,
          pauseOnHover: false,
          useCSS: false,
                          start: function(slider) {
              if (typeof(slider.slides) !== 'undefined' && slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                 
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          },
          before: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                 $f(slider.slides.eq(slider.currentSlide).find('iframe').attr('id') ).api('pause');                                           YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                  
                 /* ------------------  YOUTUBE FOR AUTOSLIDER ------------------ */
                 playVideoAndPauseOthers(slider);
             }
          },
          after: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                                                          YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          }
      });

      function playVideoAndPauseOthers(slider) {
          jQuery(slider).find('iframe').each(function(i) {
              var func = 'stopVideo';
              this.contentWindow.postMessage('{"event":"command","func":"' + func + '","args":""}', '*');
          });
      }

      /* ------------------ PREV & NEXT BUTTON FOR FLEXSLIDER (YOUTUBE) ------------------ */
      jQuery('.flex-next, .flex-prev').click(function() {
          playVideoAndPauseOthers(jQuery(this).parents('.flexslider, .tfs-slider'));
      });

      function onPlayerStateChange(frame, slider) {
          return function(event) {
              if(event.data == YT.PlayerState.PLAYING) {
                  jQuery(slider).flexslider("pause");
              }
              if(event.data == YT.PlayerState.PAUSED) {
                  jQuery(slider).flexslider("play");
              }
          }
      }
  }

  if(jQuery().isotope) {
      var gridwidth = (jQuery('.grid-layout').width() / 2) - 22;
      jQuery('.grid-layout .post').css('width', gridwidth);
      jQuery('.grid-layout').isotope({
          layoutMode: 'masonry',
          itemSelector: '.post',
          transformsEnabled: false,
          masonry: {
              columnWidth: gridwidth,
              gutterWidth: 40
          },
      });

      var gridwidth = (jQuery('.grid-full-layout').width() / 3) - 30;
      jQuery('.grid-full-layout .post').css('width', gridwidth);
      jQuery('.grid-full-layout').isotope({
          layoutMode: 'masonry',
          itemSelector: '.post',
          transformsEnabled: false,
          masonry: {
              columnWidth: gridwidth,
              gutterWidth: 40
          },
      });
  }

  jQuery('.rev_slider_wrapper').each(function() {
      if(jQuery(this).length >=1 && jQuery(this).find('.tp-bannershadow').length == 0) {
          jQuery('<div class="shadow-left">').appendTo(this);
          jQuery('<div class="shadow-right">').appendTo(this);

          jQuery(this).addClass('avada-skin-rev');
      }
  });

  jQuery('.tparrows').each(function() {
      if(jQuery(this).css('visibility') == 'hidden') {
          jQuery(this).remove();
      }
  });
});
jQuery(document).ready(function() {
  function onAfter(curr, next, opts, fwd) {
    var $ht = jQuery(this).height();

    //set the container's height to that of the current slide
    jQuery(this).parent().css('height', $ht);
  }
  if(jQuery().cycle) {
      jQuery('.reviews').cycle({
          fx: 'fade',
          after: onAfter,
                          timeout: 4000                           });
  }
});
jQuery(window).load(function($) {
  jQuery('.header-social .menu > li').height(jQuery('.header-social').height());
  jQuery('.header-social .menu > li').css('line-height', jQuery('.header-social').height()+'px');
  jQuery('.header-social .menu > li.cart').css('line-height', jQuery('.header-social').height()+'px');


  if(jQuery().prettyPhoto) {
      var ppArgs = {
                          animation_speed: 'fast',
                          overlay_gallery: true,
          autoplay_slideshow: false,
                          slideshow: 5000,
                                          opacity: 0.8,
                          show_title: true,
          show_desc: true,
                      };

      jQuery("a[rel^='prettyPhoto']").prettyPhoto(ppArgs);

      
      jQuery('.lightbox-enabled a').has('img').prettyPhoto(ppArgs);

      var mediaQuery = 'desk';

      if (Modernizr.mq('only screen and (max-width: 600px)') || Modernizr.mq('only screen and (max-height: 520px)')) {

          mediaQuery = 'mobile';
          jQuery("a[rel^='prettyPhoto']").unbind('click');
                          jQuery('.lightbox-enabled a').has('img').unbind('click');
      }

      // Disables prettyPhoto if screen small
      jQuery(window).on('resize', function() {
          if ((Modernizr.mq('only screen and (max-width: 600px)') || Modernizr.mq('only screen and (max-height: 520px)')) && mediaQuery == 'desk') {
              jQuery("a[rel^='prettyPhoto']").unbind('click.prettyphoto');
                                  jQuery('.lightbox-enabled a').has('img').unbind('click.prettyphoto');
              mediaQuery = 'mobile';
          } else if (!Modernizr.mq('only screen and (max-width: 600px)') && !Modernizr.mq('only screen and (max-height: 520px)') && mediaQuery == 'mobile') {
              jQuery("a[rel^='prettyPhoto']").prettyPhoto(ppArgs);
                                  jQuery('.lightbox-enabled a').has('img').prettyPhoto(ppArgs);
              mediaQuery = 'desk';
          }
      });
  }
          jQuery('.side-nav li').hoverIntent({
  over: function() {
      if(jQuery(this).find('> .children').length >= 1) {
          jQuery(this).find('> .children').stop(true, true).slideDown('slow');
      }
  },
  out: function() {
      if(jQuery(this).find('.current_page_item').length == 0 && jQuery(this).hasClass('current_page_item') == false) {
          jQuery(this).find('.children').stop(true, true).slideUp('slow');
      }
  },
  timeout: 500
  });
  
  if(jQuery().eislideshow) {
      jQuery('#ei-slider').eislideshow({
                          animation: 'sides',
                          autoplay: true,
                          slideshow_interval: 3000,
                                          speed: 800,
                                          thumbMaxWidth: 150                          });
  }

  var retina = window.devicePixelRatio > 1 ? true : false;

  
  /* wpml flag in center */
  var wpml_flag = jQuery('ul#nav > li > a > .iclflag');
  var wpml_h = wpml_flag.height();
  wpml_flag.css('margin-top', +wpml_h / - 2 + "px");

  var wpml_flag = jQuery('.top-menu > ul > li > a > .iclflag');
  var wpml_h = wpml_flag.height();
  wpml_flag.css('margin-top', +wpml_h / - 2 + "px");

          jQuery('#posts-container').infinitescroll({
      navSelector  : "div.pagination",
                     // selector for the paged navigation (it will be hidden)
      nextSelector : "a.pagination-next",
                     // selector for the NEXT link (to page 2)
      itemSelector : "div.post",
                     // selector for all items you'll retrieve
      errorCallback: function() {
          jQuery('#posts-container').isotope('reLayout');
      }
  }, function(posts) {
      if(jQuery().isotope) {
          //jQuery(posts).css('position', 'relative').css('top', 'auto').css('left', 'auto');

          jQuery(posts).hide();
          imagesLoaded(posts, function() {
              jQuery(posts).fadeIn();
              jQuery('#posts-container').isotope('appended', jQuery(posts));
              jQuery('#posts-container').isotope('reLayout');
          });

          var gridwidth = (jQuery('.grid-layout').width() / 2) - 22;
          jQuery('.grid-layout .post').css('width', gridwidth);

          var gridwidth = (jQuery('.grid-full-layout').width() / 3) - 30;
          jQuery('.grid-full-layout .post').css('width', gridwidth);

          jQuery('#posts-container').isotope('reLayout');
      }

      jQuery('.flexslider').flexslider({
          slideshow: true,
          slideshowSpeed: 7000,
          video: true,
          pauseOnHover: false,
          useCSS: false,
          start: function(slider) {
              if (typeof(slider.slides) !== 'undefined' && slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                 
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          },
          before: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                 $f(slider.slides.eq(slider.currentSlide).find('iframe').attr('id') ).api('pause');
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                  
                 /* ------------------  YOUTUBE FOR AUTOSLIDER ------------------ */
                 playVideoAndPauseOthers(slider);
             }
          },
          after: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                                                          YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          }
      });
      if(jQuery().prettyPhoto) { jQuery("a[rel^='prettyPhoto']").prettyPhoto(ppArgs); }
      jQuery(posts).each(function() {
          jQuery(this).find('.full-video, .video-shortcode, .wooslider .slide-content').fitVids();
      });

      if(jQuery().isotope) {
          jQuery('#posts-container').isotope('reLayout');
      }
  });
  
  jQuery('#posts-container-infinite').infinitescroll({
      navSelector  : "div.pagination",
                     // selector for the paged navigation (it will be hidden)
      nextSelector : "a.pagination-next",
                     // selector for the NEXT link (to page 2)
      itemSelector : "div.post",
                     // selector for all items you'll retrieve
      errorCallback: function() {
          jQuery('#posts-container').isotope('reLayout');
      }
  }, function(posts) {
      if(jQuery().isotope) {
          //jQuery(posts).css('top', 'auto').css('left', 'auto');

          jQuery(posts).hide();
          imagesLoaded(posts, function() {
              jQuery(posts).fadeIn();
              jQuery('#posts-container-infinite').isotope('appended', jQuery(posts));
              jQuery('#posts-container-infinite').isotope('reLayout');
          });

          var gridwidth = (jQuery('.grid-layout').width() / 2) - 22;
          jQuery('.grid-layout .post').css('width', gridwidth);

          var gridwidth = (jQuery('.grid-full-layout').width() / 3) - 30;
          jQuery('.grid-full-layout .post').css('width', gridwidth);

          jQuery('#posts-container-infinite').isotope('reLayout');
      }

      jQuery('.flexslider').flexslider({
          slideshow: true,
          slideshowSpeed: 7000,
          video: true,
          pauseOnHover: false,
          useCSS: false,
          start: function(slider) {
              if (typeof(slider.slides) !== 'undefined' && slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                 
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          },
          before: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                 $f(slider.slides.eq(slider.currentSlide).find('iframe').attr('id') ).api('pause');
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                  
                 /* ------------------  YOUTUBE FOR AUTOSLIDER ------------------ */
                 playVideoAndPauseOthers(slider);
             }
          },
          after: function(slider) {
              if (slider.slides.eq(slider.currentSlide).find('iframe').length !== 0) {
                                     jQuery(slider).find('.flex-control-nav').hide();
                 
                                      YT_ready(function() {
                      new YT.Player(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), {
                          events: {
                              'onStateChange': onPlayerStateChange(slider.slides.eq(slider.currentSlide).find('iframe').attr('id'), slider)
                          }
                      });
                  });
                                     } else {
                                     jQuery(slider).find('.flex-control-nav').show();
                                 }
          }
      });
      if(jQuery().prettyPhoto) { jQuery("a[rel^='prettyPhoto']").prettyPhoto(ppArgs); }
      jQuery(posts).each(function() {
          jQuery(this).find('.full-video, .video-shortcode, .wooslider .slide-content').fitVids();
      });

      if(jQuery().isotope) {
          jQuery('#posts-container-infinite').isotope('reLayout');
      }
  });

});

// ---------------------------


/******************************************
    -   PREPARE PLACEHOLDER FOR SLIDER  -
******************************************/


var setREVStartSize = function() {
    var tpopt = new Object();
        tpopt.startwidth = 1000;
        tpopt.startheight = 438;
        tpopt.container = jQuery('#rev_slider_1_1');
        tpopt.fullScreen = "off";
        tpopt.forceFullWidth="off";

    tpopt.container.closest(".rev_slider_wrapper").css({height:tpopt.container.height()});tpopt.width=parseInt(tpopt.container.width(),0);tpopt.height=parseInt(tpopt.container.height(),0);tpopt.bw=tpopt.width/tpopt.startwidth;tpopt.bh=tpopt.height/tpopt.startheight;if(tpopt.bh>tpopt.bw)tpopt.bh=tpopt.bw;if(tpopt.bh<tpopt.bw)tpopt.bw=tpopt.bh;if(tpopt.bw<tpopt.bh)tpopt.bh=tpopt.bw;if(tpopt.bh>1){tpopt.bw=1;tpopt.bh=1}if(tpopt.bw>1){tpopt.bw=1;tpopt.bh=1}tpopt.height=Math.round(tpopt.startheight*(tpopt.width/tpopt.startwidth));if(tpopt.height>tpopt.startheight&&tpopt.autoHeight!="on")tpopt.height=tpopt.startheight;if(tpopt.fullScreen=="on"){tpopt.height=tpopt.bw*tpopt.startheight;var cow=tpopt.container.parent().width();var coh=jQuery(window).height();if(tpopt.fullScreenOffsetContainer!=undefined){try{var offcontainers=tpopt.fullScreenOffsetContainer.split(",");jQuery.each(offcontainers,function(e,t){coh=coh-jQuery(t).outerHeight(true);if(coh<tpopt.minFullScreenHeight)coh=tpopt.minFullScreenHeight})}catch(e){}}tpopt.container.parent().height(coh);tpopt.container.height(coh);tpopt.container.closest(".rev_slider_wrapper").height(coh);tpopt.container.closest(".forcefullwidth_wrapper_tp_banner").find(".tp-fullwidth-forcer").height(coh);tpopt.container.css({height:"100%"});tpopt.height=coh;}else{tpopt.container.height(tpopt.height);tpopt.container.closest(".rev_slider_wrapper").height(tpopt.height);tpopt.container.closest(".forcefullwidth_wrapper_tp_banner").find(".tp-fullwidth-forcer").height(tpopt.height);}
};

/* CALL PLACEHOLDER */
setREVStartSize();


var tpj=jQuery;
tpj.noConflict();
var revapi1;

tpj(document).ready(function() {

if(tpj('#rev_slider_1_1').revolution == undefined)
    revslider_showDoubleJqueryError('#rev_slider_1_1');
else
   revapi1 = tpj('#rev_slider_1_1').show().revolution(
    {
        dottedOverlay:"none",
        delay:5000,
        startwidth:1000,
        startheight:438,
        hideThumbs:200,

        thumbWidth:100,
        thumbHeight:50,
        thumbAmount:5,
        
                                
        simplifyAll:"off",

        navigationType:"bullet",
        navigationArrows:"solo",
        navigationStyle:"round",

        touchenabled:"on",
        onHoverStop:"on",
        nextSlideOnWindowFocus:"off",

        swipe_threshold: 75,
        swipe_min_touches: 1,
        drag_block_vertical: false,
        
                                
                                
        keyboardNavigation:"off",

        navigationHAlign:"center",
        navigationVAlign:"bottom",
        navigationHOffset:0,
        navigationVOffset:20,

        soloArrowLeftHalign:"left",
        soloArrowLeftValign:"center",
        soloArrowLeftHOffset:20,
        soloArrowLeftVOffset:0,

        soloArrowRightHalign:"right",
        soloArrowRightValign:"center",
        soloArrowRightHOffset:20,
        soloArrowRightVOffset:0,

        shadow:0,
        fullWidth:"on",
        fullScreen:"off",

        spinner:"spinner0",
        
        stopLoop:"off",
        stopAfterLoops:-1,
        stopAtSlide:-1,

        shuffle:"off",

        autoHeight:"on",
        forceFullWidth:"off",
        
        
        hideTimerBar:"on",
        hideThumbsOnMobile:"off",
        hideNavDelayOnMobile:1500,
        hideBulletsOnMobile:"off",
        hideArrowsOnMobile:"off",
        hideThumbsUnderResolution:0,

                                hideSliderAtLimit:0,
        hideCaptionAtLimit:0,
        hideAllCaptionAtLilmit:0,
        startWithSlide:0                    });



    
}); /*ready*/


// ---------------------------------

var js_local_vars = {"dropdown_goto":""};

var mc4wp_forms_config = [];

// ---------------------------------

(function() {function addEventListener(element,event,handler) {
    if(element.addEventListener) {
        element.addEventListener(event,handler, false);
    } else if(element.attachEvent){
        element.attachEvent('on'+event,handler);
    }
}})();
