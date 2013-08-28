// Generated by CoffeeScript 1.6.3
(function() {
  describe('VideoCaption', function() {
    beforeEach(function() {
      spyOn(VideoCaption.prototype, 'fetchCaption').andCallThrough();
      spyOn($, 'ajaxWithPrefix').andCallThrough();
      return window.onTouchBasedDevice = jasmine.createSpy('onTouchBasedDevice').andReturn(false);
    });
    afterEach(function() {
      YT.Player = void 0;
      $.fn.scrollTo.reset();
      return $('.subtitles').remove();
    });
    describe('constructor', function() {
      describe('always', function() {
        beforeEach(function() {
          this.player = jasmine.stubVideoPlayer(this);
          return this.caption = this.player.caption;
        });
        it('set the youtube id', function() {
          return expect(this.caption.youtubeId).toEqual('normalSpeedYoutubeId');
        });
        it('create the caption element', function() {
          return expect($('.video')).toContain('ol.subtitles');
        });
        it('add caption control to video player', function() {
          return expect($('.video')).toContain('a.hide-subtitles');
        });
        it('fetch the caption', function() {
          expect(this.caption.loaded).toBeTruthy();
          expect(this.caption.fetchCaption).toHaveBeenCalled();
          return expect($.ajaxWithPrefix).toHaveBeenCalledWith({
            url: this.caption.captionURL(),
            notifyOnError: false,
            success: jasmine.any(Function)
          });
        });
        it('bind window resize event', function() {
          return expect($(window)).toHandleWith('resize', this.caption.resize);
        });
        it('bind the hide caption button', function() {
          return expect($('.hide-subtitles')).toHandleWith('click', this.caption.toggle);
        });
        return it('bind the mouse movement', function() {
          expect($('.subtitles')).toHandleWith('mouseover', this.caption.onMouseEnter);
          expect($('.subtitles')).toHandleWith('mouseout', this.caption.onMouseLeave);
          expect($('.subtitles')).toHandleWith('mousemove', this.caption.onMovement);
          expect($('.subtitles')).toHandleWith('mousewheel', this.caption.onMovement);
          return expect($('.subtitles')).toHandleWith('DOMMouseScroll', this.caption.onMovement);
        });
      });
      describe('when on a non touch-based device', function() {
        beforeEach(function() {
          this.player = jasmine.stubVideoPlayer(this);
          return this.caption = this.player.caption;
        });
        it('render the caption', function() {
          var captionsData,
            _this = this;
          captionsData = jasmine.stubbedCaption;
          return $('.subtitles li[data-index]').each(function(index, link) {
            expect($(link)).toHaveData('index', index);
            expect($(link)).toHaveData('start', captionsData.start[index]);
            return expect($(link)).toHaveText(captionsData.text[index]);
          });
        });
        it('add a padding element to caption', function() {
          expect($('.subtitles li:first')).toBe('.spacing');
          return expect($('.subtitles li:last')).toBe('.spacing');
        });
        it('bind all the caption link', function() {
          var _this = this;
          return $('.subtitles li[data-index]').each(function(index, link) {
            return expect($(link)).toHandleWith('click', _this.caption.seekPlayer);
          });
        });
        return it('set rendered to true', function() {
          return expect(this.caption.rendered).toBeTruthy();
        });
      });
      return describe('when on a touch-based device', function() {
        beforeEach(function() {
          window.onTouchBasedDevice.andReturn(true);
          this.player = jasmine.stubVideoPlayer(this);
          return this.caption = this.player.caption;
        });
        it('show explaination message', function() {
          return expect($('.subtitles li')).toHaveHtml("Caption will be displayed when you start playing the video.");
        });
        return it('does not set rendered to true', function() {
          return expect(this.caption.rendered).toBeFalsy();
        });
      });
    });
    describe('mouse movement', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        this.caption = this.player.caption;
        window.setTimeout.andReturn(100);
        return spyOn(window, 'clearTimeout');
      });
      describe('when cursor is outside of the caption box', function() {
        beforeEach(function() {
          return $(window).trigger(jQuery.Event('mousemove'));
        });
        return it('does not set freezing timeout', function() {
          return expect(this.caption.frozen).toBeFalsy();
        });
      });
      describe('when cursor is in the caption box', function() {
        beforeEach(function() {
          return $('.subtitles').trigger(jQuery.Event('mouseenter'));
        });
        it('set the freezing timeout', function() {
          return expect(this.caption.frozen).toEqual(100);
        });
        describe('when the cursor is moving', function() {
          beforeEach(function() {
            return $('.subtitles').trigger(jQuery.Event('mousemove'));
          });
          return it('reset the freezing timeout', function() {
            return expect(window.clearTimeout).toHaveBeenCalledWith(100);
          });
        });
        return describe('when the mouse is scrolling', function() {
          beforeEach(function() {
            return $('.subtitles').trigger(jQuery.Event('mousewheel'));
          });
          return it('reset the freezing timeout', function() {
            return expect(window.clearTimeout).toHaveBeenCalledWith(100);
          });
        });
      });
      return describe('when cursor is moving out of the caption box', function() {
        beforeEach(function() {
          this.caption.frozen = 100;
          return $.fn.scrollTo.reset();
        });
        describe('always', function() {
          beforeEach(function() {
            return $('.subtitles').trigger(jQuery.Event('mouseout'));
          });
          it('reset the freezing timeout', function() {
            return expect(window.clearTimeout).toHaveBeenCalledWith(100);
          });
          return it('unfreeze the caption', function() {
            return expect(this.caption.frozen).toBeNull();
          });
        });
        describe('when the player is playing', function() {
          beforeEach(function() {
            this.caption.playing = true;
            $('.subtitles li[data-index]:first').addClass('current');
            return $('.subtitles').trigger(jQuery.Event('mouseout'));
          });
          return it('scroll the caption', function() {
            return expect($.fn.scrollTo).toHaveBeenCalled();
          });
        });
        return describe('when the player is not playing', function() {
          beforeEach(function() {
            this.caption.playing = false;
            return $('.subtitles').trigger(jQuery.Event('mouseout'));
          });
          return it('does not scroll the caption', function() {
            return expect($.fn.scrollTo).not.toHaveBeenCalled();
          });
        });
      });
    });
    describe('search', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        return this.caption = this.player.caption;
      });
      return it('return a correct caption index', function() {
        expect(this.caption.search(0)).toEqual(0);
        expect(this.caption.search(9999)).toEqual(0);
        expect(this.caption.search(10000)).toEqual(1);
        expect(this.caption.search(15000)).toEqual(1);
        expect(this.caption.search(30000)).toEqual(3);
        return expect(this.caption.search(30001)).toEqual(3);
      });
    });
    describe('play', function() {
      return describe('when the caption was not rendered', function() {
        beforeEach(function() {
          window.onTouchBasedDevice.andReturn(true);
          this.player = jasmine.stubVideoPlayer(this);
          this.caption = this.player.caption;
          return this.caption.play();
        });
        it('render the caption', function() {
          var captionsData,
            _this = this;
          captionsData = jasmine.stubbedCaption;
          return $('.subtitles li[data-index]').each(function(index, link) {
            expect($(link)).toHaveData('index', index);
            expect($(link)).toHaveData('start', captionsData.start[index]);
            return expect($(link)).toHaveText(captionsData.text[index]);
          });
        });
        it('add a padding element to caption', function() {
          expect($('.subtitles li:first')).toBe('.spacing');
          return expect($('.subtitles li:last')).toBe('.spacing');
        });
        it('bind all the caption link', function() {
          var _this = this;
          return $('.subtitles li[data-index]').each(function(index, link) {
            return expect($(link)).toHandleWith('click', _this.caption.seekPlayer);
          });
        });
        it('set rendered to true', function() {
          return expect(this.caption.rendered).toBeTruthy();
        });
        return it('set playing to true', function() {
          return expect(this.caption.playing).toBeTruthy();
        });
      });
    });
    describe('pause', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        this.caption = this.player.caption;
        this.caption.playing = true;
        return this.caption.pause();
      });
      return it('set playing to false', function() {
        return expect(this.caption.playing).toBeFalsy();
      });
    });
    describe('updatePlayTime', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        return this.caption = this.player.caption;
      });
      describe('when the video speed is 1.0x', function() {
        beforeEach(function() {
          this.caption.currentSpeed = '1.0';
          return this.caption.updatePlayTime(25.000);
        });
        return it('search the caption based on time', function() {
          return expect(this.caption.currentIndex).toEqual(2);
        });
      });
      describe('when the video speed is not 1.0x', function() {
        beforeEach(function() {
          this.caption.currentSpeed = '0.75';
          return this.caption.updatePlayTime(25.000);
        });
        return it('search the caption based on 1.0x speed', function() {
          return expect(this.caption.currentIndex).toEqual(1);
        });
      });
      describe('when the index is not the same', function() {
        beforeEach(function() {
          this.caption.currentIndex = 1;
          $('.subtitles li[data-index=1]').addClass('current');
          return this.caption.updatePlayTime(25.000);
        });
        it('deactivate the previous caption', function() {
          return expect($('.subtitles li[data-index=1]')).not.toHaveClass('current');
        });
        it('activate new caption', function() {
          return expect($('.subtitles li[data-index=2]')).toHaveClass('current');
        });
        it('save new index', function() {
          return expect(this.caption.currentIndex).toEqual(2);
        });
        return it('scroll caption to new position', function() {
          return expect($.fn.scrollTo).toHaveBeenCalled();
        });
      });
      return describe('when the index is the same', function() {
        beforeEach(function() {
          this.caption.currentIndex = 1;
          $('.subtitles li[data-index=1]').addClass('current');
          return this.caption.updatePlayTime(15.000);
        });
        return it('does not change current subtitle', function() {
          return expect($('.subtitles li[data-index=1]')).toHaveClass('current');
        });
      });
    });
    describe('resize', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        this.caption = this.player.caption;
        $('.subtitles li[data-index=1]').addClass('current');
        return this.caption.resize();
      });
      it('set the height of caption container', function() {
        return expect(parseInt($('.subtitles').css('maxHeight'))).toBeCloseTo($('.video-wrapper').height(), 2);
      });
      it('set the height of caption spacing', function() {
        expect(Math.abs(parseInt($('.subtitles .spacing:first').css('height')) - this.caption.topSpacingHeight())).toBeLessThan(1);
        return expect(Math.abs(parseInt($('.subtitles .spacing:last').css('height')) - this.caption.bottomSpacingHeight())).toBeLessThan(1);
      });
      return it('scroll caption to new position', function() {
        return expect($.fn.scrollTo).toHaveBeenCalled();
      });
    });
    describe('scrollCaption', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        return this.caption = this.player.caption;
      });
      describe('when frozen', function() {
        beforeEach(function() {
          this.caption.frozen = true;
          $('.subtitles li[data-index=1]').addClass('current');
          return this.caption.scrollCaption();
        });
        return it('does not scroll the caption', function() {
          return expect($.fn.scrollTo).not.toHaveBeenCalled();
        });
      });
      return describe('when not frozen', function() {
        beforeEach(function() {
          return this.caption.frozen = false;
        });
        describe('when there is no current caption', function() {
          beforeEach(function() {
            return this.caption.scrollCaption();
          });
          return it('does not scroll the caption', function() {
            return expect($.fn.scrollTo).not.toHaveBeenCalled();
          });
        });
        return describe('when there is a current caption', function() {
          beforeEach(function() {
            $('.subtitles li[data-index=1]').addClass('current');
            return this.caption.scrollCaption();
          });
          return it('scroll to current caption', function() {
            return expect($.fn.scrollTo).toHaveBeenCalledWith($('.subtitles .current:first', this.caption.el), {
              offset: -($('.video-wrapper').height() / 2 - $('.subtitles .current:first').height() / 2)
            });
          });
        });
      });
    });
    describe('seekPlayer', function() {
      beforeEach(function() {
        var _this = this;
        this.player = jasmine.stubVideoPlayer(this);
        this.caption = this.player.caption;
        this.time = null;
        return $(this.caption).bind('seek', function(event, time) {
          return _this.time = time;
        });
      });
      describe('when the video speed is 1.0x', function() {
        beforeEach(function() {
          this.caption.currentSpeed = '1.0';
          return $('.subtitles li[data-start="30000"]').trigger('click');
        });
        return it('trigger seek event with the correct time', function() {
          return expect(this.time).toEqual(30.000);
        });
      });
      return describe('when the video speed is not 1.0x', function() {
        beforeEach(function() {
          this.caption.currentSpeed = '0.75';
          return $('.subtitles li[data-start="30000"]').trigger('click');
        });
        return it('trigger seek event with the correct time', function() {
          return expect(this.time).toEqual(40.000);
        });
      });
    });
    return describe('toggle', function() {
      beforeEach(function() {
        this.player = jasmine.stubVideoPlayer(this);
        this.caption = this.player.caption;
        return $('.subtitles li[data-index=1]').addClass('current');
      });
      describe('when the caption is visible', function() {
        beforeEach(function() {
          this.caption.el.removeClass('closed');
          return this.caption.toggle(jQuery.Event('click'));
        });
        return it('hide the caption', function() {
          return expect(this.caption.el).toHaveClass('closed');
        });
      });
      return describe('when the caption is hidden', function() {
        beforeEach(function() {
          this.caption.el.addClass('closed');
          return this.caption.toggle(jQuery.Event('click'));
        });
        it('show the caption', function() {
          return expect(this.caption.el).not.toHaveClass('closed');
        });
        return it('scroll the caption', function() {
          return expect($.fn.scrollTo).toHaveBeenCalled();
        });
      });
    });
  });

}).call(this);
