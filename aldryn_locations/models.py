from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible


@python_2_unicode_compatible
class MapPlugin(CMSPlugin):
    ROADMAP = 'roadmap'
    SATELLITE = 'satellite'
    HYBRID = 'hybrid'
    TERRAIN = 'terrain'

    MAP_CHOICES = (
        (ROADMAP, _('Roadmap')),
        (SATELLITE, _('Satellite')),
        (HYBRID, _('Hybrid')),
        (TERRAIN, _('Terrain')),
    )

    title = models.CharField(_("map title"), max_length=100, blank=True,
                             null=True)

    ZOOM_LEVELS = map(lambda c: (c, str(c)), range(22))

    zoom = models.CharField(
        _('zoom level'), choices=ZOOM_LEVELS, blank=True, null=True,
        help_text=_('Leave empty for auto zoom'), max_length=20)

    route_planner_title = models.CharField(
        _('Route Planner Title'), max_length=150, blank=True, null=True,
        default=_('Calculate your fastest way to here'))

    width = models.CharField(
        _('width'), max_length=6, default='100%',
        help_text=_('Plugin width (in pixels or percent).'))

    height = models.CharField(
        _('height'), max_length=6, default='400px',
        help_text=_('Plugin height (in pixels).'))

    scrollwheel = models.BooleanField(
        _('Enable scrollwheel zooming on the map'), default=True)

    double_click_zoom = models.BooleanField(
        _('Enable double click to zoom'), default=True)

    draggable = models.BooleanField(_('Allow map dragging'), default=True)

    keyboard_shortcuts = models.BooleanField(
        _('Enable keyboard shortcuts'), default=True)

    pan_control = models.BooleanField(_('Show pan control'), default=True)

    zoom_control = models.BooleanField(_('Show zoom control'), default=True)

    street_view_control = models.BooleanField(
        _('Show Street View control'), default=True)

    map_type = models.CharField(_('Map Type'), max_length=300, choices=MAP_CHOICES, default=ROADMAP)

    def __str__(self):
        ret = ''

        if self.child_plugin_instances:
            locs = routes = 0
            for location in self.child_plugin_instances:
                if location.route_planner:
                    routes += 1
                else:
                    locs += 1

            if locs:
                if locs == 1:
                    _loc = _('Location')
                else:
                    _loc = _('Locations')

                if routes:
                    ret = u' (%i %s & %i %s)' % (locs, _loc, routes, _('Route'))
                else:
                    ret = u' (%i %s)' % (locs, _loc)

            elif routes:
                ret = u' (%i %s)' % (routes, _('Route'))

        return u'%s%s' % (self.title or _('Map'), ret)

    def get_route_planner(self):
        if self.child_plugin_instances:
            for location in self.child_plugin_instances:
                if location.route_planner:
                    return location.address, location.zipcode, location.city
        return False


@python_2_unicode_compatible
class LocationPlugin(CMSPlugin):
    address = models.CharField(_("address"), max_length=150)
    zipcode = models.CharField(_("zip code"), max_length=30)
    city = models.CharField(_("city"), max_length=100)

    content = models.CharField(
        _("additional content"), max_length=255, blank=True,
        help_text=_('Displayed under address in the bubble.'))

    lat = models.DecimalField(
        _('latitude'), max_digits=10, decimal_places=6, null=True, blank=True,
        help_text=_('Use latitude & longitude to fine tune the map position.'))

    lng = models.DecimalField(
        _('longitude'), max_digits=10, decimal_places=6, null=True, blank=True)

    @property
    def route_planner(self):
        return False

    def get_lat_lng(self):
        if self.lat and self.lng:
            return self.lat, self.lng

    def __str__(self):
        return u'%s, %s %s' % (self.address, self.zipcode, self.city)


class RouteLocationPlugin(LocationPlugin):
    @property
    def route_planner(self):
        return True
