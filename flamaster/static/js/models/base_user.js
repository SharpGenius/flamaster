// Generated by CoffeeScript 1.3.1
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

define(['chaplin/mediator', 'chaplin/model'], function(mediator, Model) {
  'use strict';

  var BaseUser;
  return BaseUser = (function(_super) {

    __extends(BaseUser, _super);

    BaseUser.name = 'BaseUser';

    function BaseUser() {
      return BaseUser.__super__.constructor.apply(this, arguments);
    }

    BaseUser.prototype.emailRegex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

    BaseUser.prototype.urlRoot = '/account/sessions/';

    BaseUser.prototype.defaults = {
      email: ''
    };

    BaseUser.prototype.initialize = function() {
      return console.log("User#initialize", this.urlRoot);
    };

    BaseUser.prototype.validate = function(attrs) {
      var response;
      response = {
        status: 'success'
      };
      if (!this.emailRegex.test(attrs.email)) {
        response = {
          status: 'failed',
          email: 'This is not valid email address'
        };
      }
      return response.status !== 'success' && response || null;
    };

    BaseUser.prototype.dispose = function() {
      var deffered;
      deffered = $.ajax({
        url: "/account/sessions/" + (encodeURI(this.get('accessToken'))),
        type: 'delete',
        complete: function() {
          return mediator.router.route('/');
        }
      });
      return BaseUser.__super__.dispose.apply(this, arguments);
    };

    return BaseUser;

  })(Model);
});
