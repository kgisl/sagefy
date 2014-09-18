###
The app takes a series of adapters, and delegates URLs
to them when the URL changes.
###

###
TODO:
- write tests
###

Events = require('./events')
_ = require('./utilities')
history = window.history

class Application extends Events
    # The application instance takes a list of adapters
    constructor: (@Adapters...) ->
        super()
        @bindAdapter(Adapter) for Adapter in Adapters
        @bindPopState()

    # Provide the navigate function to each of the adapters
    bindAdapter: (Adapter) ->
        Adapter::navigate = @navigate

    # Remove the navigate function so the adapter can be cleanly removed
    unbindAdapter: (Adapter) ->
        Adapter::navigate = null

    # Find the adapter matching the path
    findAdapter: (path) ->
        for Adapter in @Adapters
            if (_.isString(A.url) and A.url is path) or
               (_.isRegExp(A.url) and A.url.match(path))
                return Adapter

    # Navigate the application to a specific URL
    navigate: (path) ->
        # Don't navigate if we're already on the path
        if path is window.location.pathname
            return

        return @route(path)

    # Route to a new adapter, given a path
    # The new adapter is constructed and the
    # previous adapter is removed.
    route: (path) ->
        # Find the matching adapter
        Adapter = @findAdapter(path)

        # If no matching adapter, throw an error
        if not Adapter
            throw new Error("No matching adapter for path: #{path}")

        # Remove previous adapter instance
        @adapter.remove() if @adapter

        # Create a new adapter instance
        @adapter = new Adapter()

        # Update the display of the URL
        history.pushState({}, '', path)

    # When the user uses their back and forward buttons,
    # we need to listen to those events
    bindPopState: ->
        # Ensure we don't overwrite any previous `onpopstate` call
        prev = window.onpopstate if window.onpopstate
        window.onpopstate = (event) ->
            prev(event)
            @route(window.location.pathname)

    # Removes the application
    remove: ->
        super()
        @unbindAdapter(Adapter) for Adapter in Adapters

module.exports = Application
