define ['cs!channels_utils', 'cs!fixtures'], (channels_utils, Fixtures) ->
    class DataSource

        checkIntervalForUnusedCollections: 10000
        default_max_refresh_factor: 10

        constructor: ->
            @config = App.DataSourceConfig

            # Pre-process channel definitions in order to factor in
            # channel templates. This will allow us to write less
            # for very similar channels and group the common properties
            # together.
            #
            # Moreover, channel templates support the notion of parent,
            # so that there is actually a 3-level hierarchy:
            # parent of channel template - channel template - channel def
            for k, v of @config.channel_templates
                if v.parent
                    if not (v.parent of @config.channel_templates)
                        logger.error("Channel template #{k} has invalid parent #{v.parent}")
                        continue
                    parent = @config.channel_templates[v.parent]
                    @config.channel_templates[k] = _.extend({}, parent, v)

            for k, v of @config.channel_types
                if v.template
                    if not (v.template of @config.channel_templates)
                        logger.error("Channel type #{k} has invalid template #{v.template}")
                        continue
                    template = @config.channel_templates[v.template]
                    @config.channel_types[k] = _.extend({}, template, v)

        initialize: ->
            logger.info "Initializing data source"

            # Create a big collection hash which stores all the models,
            # collections and data which will be rendered
            @data = {}
            @meta_data = {}

            # Setting this to false will cause all fetches to perform
            # synchronous ajax requests (used only for testing).
            @_async_fetches = true

            # Subscribe DataSource to the new widget channel.
            # This will make it subscribe widgets to changes for the data they are monitoring.
            @pipe = loader.get_module('pubsub')

            # Requests for new data channels (coming from widgets / controllers).
            @pipe.subscribe('/new_data_channels', @newDataChannels)

            # Announcements that new widgets are available
            # This binds the widgets' methods to the proper channel events
            # (we need this because channels are private to the DataSource)
            @pipe.subscribe('/new_widget', (data) => @newWidget(data))

            # Announcements that widgets were removed
            # This binds the widgets' methods to the proper channel events
            # (we need this because channels are private to the DataSource)
            @pipe.subscribe('/destroy_widget', (data) => @destroyWidget(data))
            setInterval(@checkForUnusedCollections, @checkIntervalForUnusedCollections)

            # Requests for scrolling channels
            @pipe.subscribe('/scroll', @pushDataAfterScroll)

            # Requests for refreshing data of a given channel
            @pipe.subscribe('/refresh', @pushDataAfterRefresh)

            # Requests for modifying a given data channel
            @pipe.subscribe('/modify', @modifyDataChannel)

            # Requests for adding new data to a given channel
            @pipe.subscribe('/add', @addToDataChannel)

            # Requests for deleting data from a given channel
            @pipe.subscribe('/delete', @deleteFromDataChannel)

        _getConfig: (channel) =>
            ###
                Returns the configuration for a given channel.
            ###

            # Get the channel key. This is where the actual data is in @data
            channel_key = channels_utils.getChannelKey(channel)

            # Use @meta_data to find out the actual type of this channel
            channel_type = @meta_data[channel_key].type

            # Finally, retrieve channel type configuration
            @config.channel_types[channel_type]

        _getType: (channel) =>
            ###
                Returns the channel type: relational / api / etc.
            ###
            @_getConfig(channel).type

        _getWidgetMethod: (fake_channel, widget) =>
            ###
                Gets the appropriate function from the widget to be called
                whenever events on channel occur.

                channel: the channel on which events occur
                widget: a widget instance
                Returns: an actual function from the widget instance
            ###

            # Get the channel key. This is where the actual data is in @data
            channel_key = channels_utils.getChannelKey(fake_channel)

            # Get the method name
            method_name = channels_utils.widgetMethodForChannel(widget, channel_key)

            # Return the actual method
            widget[method_name]

        _getDefaultParams: (channel) =>
            ###
                Returns the default HTTP params for a given channel.
                This feature is only supported by relational channels for now.

                For API channels, the default_value has a completely different
                meaning: the default value of the JSON data.

                TODO(andrei): refactor this to be less dumb
            ###

            type = @_getType(channel)
            # We only support HTTP params for channels of type relational
            if type != 'relational'
                return {}
            conf = @_getConfig(channel)
            conf.default_value or {}

        _fetchChannelDataFromServer: (channel, reason='refresh', callback=null) =>
            ###
                Fetch the data for the channel given the params.

                channel: the given channel. The HTTP parameters for fetching
                         the channel data are taken from @meta_data[channel].params
                reason: 'refresh' (default), 'streampoll' or 'scroll'
                callback: a (channel_guid, success) function that will
                          be called after the fetch is complete
                Returns: nothing
            ###
            # Sanity check - the only valid reasons for fetching data are
            # 'refresh', 'scroll' and 'streampoll'.
            if not (reason in ['refresh', 'scroll', 'streampoll'])
                throw "Invalid reason: #{reason}"
                return

            conf = @_getConfig(channel)
            channel_key = channels_utils.getChannelKey(channel)
            meta = @meta_data[channel_key]
            # Streampoll doesn't increment waiting fetch count.
            # Otherwise, when changing tabs periodic requests for new
            # mentions will NEVER stop, which is just plain wrong.
            if reason != 'streampoll'
                waiting_fetches = if meta.waiting_fetches then meta.waiting_fetches else 0
                meta.waiting_fetches = waiting_fetches + 1

            # Build the current parameters. For normal requests,
            # they are the current default values overlapped with
            # the current values (found in @meta_data[channel_key]).
            default_value = @_getDefaultParams(channel)
            params = _.extend({}, default_value, meta.params)

            # If we're fetching on behalf of a scroll / streampoll request,
            # make sure that we give the scroll/streampoll_params function
            # the opportunity to modify the current HTTP params.
            if reason in ['scroll', 'streampoll']
                fn_name = reason + '_params'
                if not (fn_name of conf)
                    logger.error("Configuration for channel #{channel_key} should have function #{fn_name}")
                    return
                # Retrieve the new parameters
                params = conf[fn_name](@data[channel_key], params)
                if not params
                    # Cancel the current streampoll/scroll request if params == null.
                    # Careful - emtpy dict { } evaluates to true in JavaScript!
                    return

            # See if this channel has an associated URL. If it doesn't,
            # just load it from fixtures.
            if not ('url' of conf)
                @_loadFixtures(channel_key, params)
                @_checkForNewlyArrivedAndAwaitedModels(channel_key)
                # Fixture channels are fetched synchronously, no need to
                # call _fillWaitingChannels
                meta.last_fetch = Utils.now()
                callback(channel_key, true) if callback
                return meta.last_fetch

            # If the encode_POST_as_JSON flag is set, instead of URL-encoding
            # the parameters as for normal forms, send them encoded as JSON.
            if conf.fetch_through_POST and conf.encode_POST_as_JSON
                params_for_fetch = JSON.stringify(params)
            else
                params_for_fetch = _.clone(params)

            # Channel has an associated URL. Fetch data from that URL.
            fetch_params =
                async: @_async_fetches
                # Don't add models on refresh (reset entire collection instead).
                add: reason != 'refresh'
                # For POST requests, the URL should contain no extra GET params,
                # and those params should rather be sent through POST data.
                # This is because we might have large data to POST,
                # and as we all know, the GET URI has a pretty low length limit.
                type: if conf.fetch_through_POST then 'POST' else 'GET'
                data: if conf.fetch_through_POST then params_for_fetch else {}

            # When the data is encoded as JSON, be careful to set the correct
            # content-type.
            if conf.fetch_through_POST and conf.encode_POST_as_JSON
                fetch_params.contentType = 'application/json'

            # Story behind this decision to insert a fetched callback before triggering reset:
            # When you are binding a widget to a collection (datasource._bindWidgetToRelationalChannel)
            # you are doing 2 things:
            # 1. widget is subscribed to all collection events ('reset' included):
            #    - if collection is updated then the widget is notified to refresh contents
            # 2. if the collection is already filled: @meta_data[collection].last_fetch?
            #    then the widget is notified to refresh contents
            # With a fetched event before reset you are setting meta.last_fetch eliminating a race condition
            # where 'reset' event will cause a bindWidgetToRelationalChannel
            # the step 2 above will find last_fetch null thus leaving the widget empty
            fetch_params.fetched = =>
                meta.firstTimeFetch = !meta.last_fetch?
                meta.last_fetch = Utils.now()
            # Define success & error functions as wrappers around callback.
            fetch_params.success = (collection, response) =>
                @_checkForNewlyArrivedAndAwaitedModels(channel_key)

                # Only fill waiting channels the first time this
                # channel receives data.
                if meta.firstTimeFetch
                    @_fillWaitingChannels(channel_key)
                if reason != 'streampoll'
                    meta.waiting_fetches = meta.waiting_fetches - 1

                # Call the post fetching callback if the collection
                # has one set
                if _.isFunction(collection.postFetch)
                    collection.postFetch(response)

                callback(channel_key, true) if callback
            fetch_params.error = (collection, response) =>
                callback(channel_key, false) if callback

            # What channel should receive the data we're about to fetch -
            # the original channel, or that channel's buffer?
            # (The first fetch should always be into the real channel).
            if reason == 'streampoll' and @_getBufferSize(channel) and @meta_data[channel_key].last_fetch?
                receiving_channel = @data[channel_key].buffer
                # If the buffer is full, avoid doing any more fetches.
                if receiving_channel.length >= conf.buffer_size
                    return
            else
                receiving_channel = @data[channel_key]

            # Render the URL to which we're GET-ing or POST-ing.
            receiving_channel.url = Utils.render_url(conf.url, params, [], conf.fetch_through_POST)
            # Trigger a custom invalidate event before fetching the
            # collection from the server (invalidate gets triggered
            # every time a request is made to the server). The format
            # of the event is: model, collection
            receiving_channel.trigger('invalidate', null, receiving_channel)
            receiving_channel.fetch(fetch_params)

        _flushChannelBuffer: (channel_guid) =>
            ###
                Flush channel buffer by moving buffer data into channel data,
                then reset buffer.
            ###
            logger.info "Flushing channel #{channel_guid} buffer"
            channel = @data[channel_guid]

            conf = @_getConfig(channel_guid)
            # Get where to append the buffered items: 'begin' or 'end'
            add_to = conf.streampoll_add_to || 'end'
            # Get the field after which to sort the buffer items
            sort_field = conf.streampoll_sort_field

            # Sort the buffer items before flushing
            channel.buffer.models = _.sortBy(channel.buffer.models, (model) -> model.get(sort_field)) if sort_field?
            # If we add to the beginning, we take the elements in reverse order
            # from the buffer and add each element to the beginning.
            if add_to == 'begin'
                while channel.buffer.length > 0
                    model = channel.buffer.shift()
                    channel.unshift(model)
            # Otherwise, just append the whole buffer to the end of the collection
            else if add_to == 'end'
                # Add all models from buffer into channel, without event silencing.
                channel.add(channel.buffer.models)
                # Reset buffer without triggering any events.
                channel.buffer.reset([])

            @_restartRefreshing(channel_guid)

        _restartRefreshing: (channel_guid) ->
            # Restart the refreshing cycle. When refresh = 'backoff' and the
            # buffer is full, the backoff will be maxed out. Restarting will
            # also reset the buffer to its minimum value, and renew
            # the refreshing cycle.
            @_stopRefreshing(channel_guid)
            @_startRefreshing(channel_guid)

        _getRefreshInterval: (channel) =>
            ###
                Returns the periodic refresh interval for a given channel.

                channel: the channel to check
                Returns: the interval ifthe channel has periodic refresh
                         configured, 0 otherwise
            ###
            conf = @_getConfig(channel)
            if conf.refresh and 'refresh_interval' of conf
                return conf.refresh_interval
            else
                return 0

        _getMaxRefreshInterval: (channel) =>
            ###
                Returns the maximum refresh interval for a given channel -
                defaults to default_max_refresh_factor x refresh intreval.
            ###
            conf = @_getConfig(channel)
            if conf.max_refresh_interval
                return conf.max_refresh_interval
            else
                return @default_max_refresh_factor * @_getRefreshInterval(channel)

        _getRefreshType: (channel) =>
            ###
                Returns the refesh type for a given channel:
                'refresh' (default), 'streampoll', or 'scroll'.
            ###
            return @_getConfig(channel).refresh_type or "refresh"

        _getBufferSize: (channel) =>
            ###
                Returns the buffer size for a given channel (0 for no buffer).
            ###
            conf = @_getConfig(channel)
            # Only streampoll channels may have buffers.
            if conf.refresh_type == 'streampoll' and conf.buffer_size?
                return conf.buffer_size
            else
                return 0

        _startRefreshing: (channel) =>
            ###
                Start the refreshing policy for the given channel:
                periodic or backoff.
            ###
            channel_key = channels_utils.getChannelKey(channel)

            # Make sure this channel needs to be refreshed.
            refresh_interval = @_getRefreshInterval(channel_key)
            if not refresh_interval
                return

            # Make sure we don't do setTimeout() more than once per channel.
            if @meta_data[channel_key].refreshing
                return

            # Mark the fact that we're refreshing.
            @meta_data[channel_key].refreshing = true

            # Initialize backoff.
            if @_getConfig(channel_key).refresh == 'backoff'
                @meta_data[channel_key].backoff = 1

            @_scheduleNextRefresh(channel_key, true)

        _stopRefreshing: (channel_key) =>
            ###
                Cancel the current refresh request, and stop future ones
                for the given channel.
            ###
            # Stop future refresh requests.
            @meta_data[channel_key].refreshing = false
            # Stop the current refresh request (if any).
            if @meta_data[channel_key].timeout_variable
                clearTimeout(@meta_data[channel_key].timeout_variable)

        _scheduleNextRefresh: (channel_key, success) =>
            ###
                Schedule the next refresh for a given channel and a reason.
                The next refresh will call this function again via callback,
                to schedule the next refresh after that, and so on.
            ###
            # Are we still refreshing this channel?
            if not @meta_data[channel_key].refreshing
                return

            # Basic refresh_after.
            refresh_after = @_getRefreshInterval(channel_key)

            # Do not apply the backoff algorithm to fetching failures.
            if @_getConfig(channel_key).refresh == 'backoff' and success
                # Current item count = data + buffer
                current_item_count = @data[channel_key].length
                if 'buffer' of @data[channel_key]
                    current_item_count += @data[channel_key].buffer.length

                # If there are no new items, increment backoff, otherwise reset it.
                if current_item_count == @meta_data[channel_key].last_item_count
                    # Initialize the exponential backoff to 1, then double it.
                    if not @meta_data[channel_key].backoff
                        @meta_data[channel_key].backoff = 1
                    @meta_data[channel_key].backoff *= 2
                    refresh_after *= @meta_data[channel_key].backoff
                    # Ensure refresh_after < max_refresh_interval.
                    refresh_after = Math.min(refresh_after, @_getMaxRefreshInterval(channel_key))
                    logger.info "Refreshing #{channel_key} after #{refresh_after}ms"
                else
                    # Some new items, reset backoff.
                    @meta_data[channel_key].backoff = 1
                    logger.info "Reset backoff for #{channel_key}"

                # TODO(mihnea): if a scroll down event is triggered, the number
                # of items in the channel will increase, regardless of the
                # refreshing logic. This will be perceived as "new data" and
                # we might refresh sooner than needed because of it.
                # Possible fix: recompute last_item_count after each
                # reason='scroll' refresh.
                # Update last_item_count.
                @meta_data[channel_key].last_item_count = current_item_count

            # Configure periodic refresh with reason="refresh" or "streampoll"
            # (or "scroll", but that makes very little sense).
            refresh_type = @_getRefreshType(channel_key)
            handle = setTimeout((=> @_fetchChannelDataFromServer(channel_key, refresh_type, @_scheduleNextRefresh)),
                                refresh_after)
            @meta_data[channel_key].timeout_variable = handle

        _initRelationalChannel: (name, type, params) =>
            ###
                Initialize a relational channel.

                A relational channel is backed by a Backbone collection. This
                will dynamically load the collection class via require.js,
                create an instance of the collection class and perform
                final channel initialization logic.
            ###

            # Load the collection class via require.js
            collection_name = @config.channel_types[type].collection or type[1..]
            collection_module = "cs!collection/" + collection_name

            require [collection_module], (collection_class) =>
                @data[name] = new collection_class()
                conf = @config.channel_types[type]
                eternal = params['__eternal__']?
                delete params['__eternal__'] if eternal
                @meta_data[name] =
                    type: type
                    params: params
                    eternal: eternal
                    collection_class: collection_class
                    model_class: @data[name].model
                if conf.populate_on_init and params._initial_data_
                    # Avoid creating empty models
                    if not _.isEmpty(params._initial_data_)
                        @data[name].add(params._initial_data_)
                    delete params._initial_data_
                    # The url of a collection is set after fetching server
                    # data, but for collections with initial data the fetch
                    # branch is not executed. Set the url here.
                    default_value = @_getDefaultParams(name)
                    url_params = _.extend({}, default_value, params)
                    if conf.url?
                        @data[name].url = Utils.render_url(conf.url, url_params)
                # Initialize buffer.
                if conf.buffer_size? and conf.buffer_size
                    @data[name].buffer = new collection_class()
                    # Give access to the collection from the buffer
                    @data[name].buffer.collection = @data[name]
                @_finishChannelInitialization(name)

        _initApiChannel: (name, type, params) =>
            ###
                Initialize an API channel.

                This will only create a raw data object instantly and perform
                final channel initialization logic.
            ###
            # Load the collection class via require.js
            collection_name = @config.channel_types[type].collection or 'raw_data'
            collection_module = "cs!collection/" + collection_name

            require [collection_module], (collection_class) =>
                @data[name] = new collection_class()
                conf = @config.channel_types[type]
                eternal = params['__eternal__']?
                delete params['__eternal__'] if eternal
                @meta_data[name] =
                    type: type
                    params: params
                    eternal: eternal
                    collection_class: collection_class
                # If there is a default value for this channel, set it.
                if 'default_value' of conf
                    @data[name].setDefaultValue(conf.default_value)
                # If the populate_on_init flag is set for this channel, then
                # the parameters sent when creating the channel serve as initial values.
                if conf.populate_on_init
                    @data[name].set(params)
                @_finishChannelInitialization(name)

        _getChannelDuplicates: (channel_guid) =>
            ###
                Determines all duplicates of some channel. Returns a list
                of channel_guids, or an empty list, if not duplicates are found.
            ###
            duplicates = [ ]
            channel_data = @meta_data[channel_guid]
            for other_channel_guid, other_channel_data of @meta_data
                if channel_guid != other_channel_guid and
                   channel_data.type == other_channel_data.type and
                   _.isEqual(channel_data.params, other_channel_data.params)
                    duplicates.push(other_channel_guid)
            return duplicates

        _cloneChannel: (channel_guid, source_channel_guid) =>
            ###
                Clones the source channel to channel_guid.
            ###
            logger.info "Cloning #{channel_guid} from #{source_channel_guid}"
            @meta_data[channel_guid].cloned_from = source_channel_guid
            # Mark the new clone as having been recently fetched.
            @meta_data[channel_guid].last_fetch = @meta_data[source_channel_guid].last_fetch
            dest = @data[channel_guid]
            source = @data[source_channel_guid]
            channel_type = @_getType(channel_guid)
            if channel_type == 'relational'
                # Clone model without triggering any events.
                silence = { silent: true }
                for model in source.models
                    dest.add(model.clone(), silence)
                # Trigger the golden news
                dest.trigger('reset', dest)
                # Clone buffer
                if 'buffer' of source
                    for model in source.buffer.models
                        dest.buffer.add(model.clone(), silence)
                # Clone url property
                if 'url' of source
                    dest.url = source.url
            else if channel_type == 'api'
                dest.set(source.data)

        _fillWaitingChannels: (channel_guid) =>
            ###
                Try to fill each waiting channel that is a duplicate of
                this one.
            ###
            duplicates = @_getChannelDuplicates(channel_guid)
            for dest_channel_guid in duplicates
                if not @meta_data[dest_channel_guid].last_fetch?
                    # If dest_channel does not yet have data, clone into it
                    # by using this channel as clone source.
                    @_cloneChannel(dest_channel_guid, channel_guid)

        _finishChannelInitialization: (channel_guid) =>
            ###
                Channel initialization ends with one of the following outcomes,
                depending on existence of channel duplicates:
                    1) if no duplicates exist => fetch
                    2) if duplicates exist and some have data => clone
                    3) if duplicates exist but none have data => wait
                Waiting for data only happens when a duplicate exists that
                does not have data (yet). That channel is currently waiting
                for data (in fetching state), and when it receives data, it
                will fill this channel as well (via _fillWaitingChannels).
            ###
            # Get the channel's start_immediately configuration. It tells us
            # whether we should fetch channel data from server right after
            # channel instantiation. Defaults to true
            start_immediately = @_getConfig(channel_guid).start_immediately
            if not start_immediately?
                start_immediately = true

            # Cloning / fetching logic:
            duplicates = @_getChannelDuplicates(channel_guid)
            if duplicates.length == 0 or @_getConfig(channel_guid).disable_clone
                # 1) No channel duplicates exist, perform fetch.
                refresh_interval = @_getRefreshInterval(channel_guid)
                if refresh_interval > 0
                    if start_immediately
                        # Fetch the initial data for the channel
                        @_fetchChannelDataFromServer(channel_guid)
                else
                    # Fetch the initial data for the channel
                    if (not @_getConfig(channel_guid).populate_on_init) and start_immediately
                        @_fetchChannelDataFromServer(channel_guid)
                    else
                        # If this channel was populated on init, mark it
                        # as having data.
                        @meta_data[channel_guid].last_fetch = Utils.now()
            else
                # If at least one duplicate was fetched (has data), use it
                # as a cloning source. Otherwise, this channel will wait
                # for data.
                duplicate_channel_guid = null
                for other_channel_guid in duplicates
                    if @meta_data[other_channel_guid].last_fetch?
                        duplicate_channel_guid = other_channel_guid
                        break
                if duplicate_channel_guid
                    @_cloneChannel(channel_guid, duplicate_channel_guid)
                else
                    logger.info "Channel #{channel_guid} is waiting for data"

            # Setup periodic refresh if needed.
            @_startRefreshing(channel_guid)

            # Announce widget starter a new channel is available
            @pipe.publish('/initialized_channel', {name: channel_guid})

        newDataChannels: (channels) =>
            ###
                Create some new data channels on-demand.

                Controllers and widgets usually issue this kind of request,
                in order to decide which data sources to "glue" to their
                subordinated widgets on their page.
            ###

            logger.info "Initializing new channels in DataSource"
            for channel_guid, channel_data of channels
                do(channel_guid, channel_data) =>
                    # If the channel is already initialized, do nothing,
                    # otherwise initialize the associated collection.
                    if channel_guid of @data
                        return

                    logger.info("Initializing channel #{channel_guid}")

                    channel_type = channel_data.type
                    channel_params = _.clone(channel_data.params)

                    # Cannot use @_getType() because channel doesn't exist yet.
                    if channel_type of @config.channel_types
                        resource_type = @config.channel_types[channel_type].type
                        if resource_type == 'relational'
                            @_initRelationalChannel(channel_guid, channel_type, channel_params)
                        else if resource_type == 'api'
                            @_initApiChannel(channel_guid, channel_type, channel_params)
                    else
                        logger.error("Trying to initialize channel of unknown type: #{channel_type}")

        _findAndModifyRelationalChannelModel: (channel_guid, item, dict, options = {}) ->
            ###
                Implementation of modifyDataChannel specific for relational channels.
                We want to update (append, reset or exclude) attributes of a
                model which is a part of a collection. We perform an implicit save
                after we update the attributes. Because the save might fail we don't
                want to trigger any change events on the collection/model before knowing
                the new attributes are valid. We clone the individual model and
                perform the update and then the save on the clone.
                After the save is successful (only if we have to sync with the server)
                in the success callback we set the new attributes again and
                we let the change events propagate on the collection
            ###

            _.defaults(options, {sync: true, silent: false, filter: {}})
            collection = @data[channel_guid]

            filtered_models = if item is 'all' then collection.filter_by(options.filter) else [collection.get(item)]

            # If it's a relational channel backed by a fixture
            unless 'url' of @_getConfig(channel_guid)
                (individual_model.set(dict) if individual_model) for individual_model in filtered_models
                return

            for individual_model in filtered_models
                @_findAndModifyCollectionModel(collection, individual_model, dict, options) if individual_model
            # Also look for item in buffer, and modify it if it exists.
            if @_getBufferSize(channel_guid)
                filtered_models_in_buffer = if item is 'all' then collection.buffer.filter_by(options.filter) else [collection.buffer.get(item)]
                for individual_model in filtered_models_in_buffer
                    @_findAndModifyCollectionModel(collection.buffer, individual_model, dict, _.extend(options, {sync: false})) if individual_model

        _findAndModifyCollectionModel: (collection, individual_model, dict, options) ->
            ###
                Modifies the individual_model passed in arguments.
            ###

            [update_mode, sync, silent] = [options.update_mode, options.sync, options.silent]

            # Clone the individual model and set it's urlRoot property
            # because the clone won't be part of the collection. This way
            # we have a proper model url
            cloned_model = individual_model.clone()
            cloned_model.urlRoot = collection.url
            cloned_model.collection = collection

            # Perform a save on the model and propagate any error events
            # received from the server on the model's channel. If the
            # save is successful update the collection's model (individual_model)
            # with the new values of the clone (this will trigger the change events
            # after the save is ok). Otherwise trigger the errors on the individual
            # model
            if sync
                # Update clone without triggering any change events (won't matter
                # though because the clone is not part of a collection)
                cloned_model = @_updateRelationModel(cloned_model, dict, update_mode)
                # Trigger a custom invalidate event before the
                # model is saved to the server. Backbone.Model emits
                # a sync event if the save was successful. The invalidate
                # event has the following signature:
                # 'invalidate', model, collection
                individual_model.trigger('invalidate', individual_model, collection)
                options =
                    error: (model, response, options) =>
                        individual_model.trigger('error', model, response)
                    success: (model, response) =>
                        # Update model with attributes to sync from response.
                        @syncModelWithResponse(model, response)
                        options = {'silent': silent}
                        individual_model.set(model.attributes, options)

                # Note: passing silent = true to this will only cause
                # the cloned model to be updated silently, which doesn't
                # matter anyway, because no widget ever knows about it.
                cloned_model.save(cloned_model.attributes, options)
            else
                # TODO: For consistency should we trigger invalidate here as well?
                # If we don't need to sync with the server we can just update
                # the model reference in the collection and now trigger
                # the change events
                @_updateRelationModel(individual_model, dict, update_mode, silent)

        _updateRelationModel: (model, dict, update_mode, silent = true) ->
            ###
                Update a provided model with the dict arguments bypassing
                events triggering using the silent argument.
            ###
            silence = { silent: silent }
            if update_mode == 'append'
                for k, v of dict
                    # If the attribute of the model is an array
                    # then push the non array value. If the value is an
                    # array set the attribute as a list
                    if _.isArray(model.get(k))
                        current_attribute_value = model.get(k)
                        # If the value to be set is actually a list,
                        # set it directly, otherwise push it
                        if _.isArray(v)
                            current_attribute_value = v
                        else
                            current_attribute_value.push(v)
                        model.set(k, current_attribute_value)
                        # Trigger manually the change event for an
                        # Array value as Backbone.set won't trigger it
                        # TODO: patch Backbone do detect changes in
                        # Array like attributes
                        model.trigger('change', model)
                    else
                        model.set(k, v, silence)
            else if update_mode == 'reset'
                model.clear(silent)
                model.set(dict, silence)
            else if update_mode == 'exclude'
                for k of dict
                    if $.isPlainObject(k)
                        logger.error("Trying to unset a dictionary instead of a key")
                    model.unset(k, silence)
            return model

        _modifyApiDataChannel: (channel_guid, dict, update_mode) ->
            ###
                Implementation of modifyDataChannel specific for api channels.
            ###

            model = @data[channel_guid]
            if update_mode == 'append'
                model.set(dict)
            else if update_mode == 'reset'
                model.set(dict, null, {reset: true})
            else if update_mode == 'exclude'
                model.unset(dict)

        modifyDataChannel: (channel, dict, options = {}) =>
            ###
                Modifies the data found at channel by calling
                data.set(k, v) for each pair (k, v) of dict.

                @param {String}     channel                 The channel on which to modify objects
                @param {Object}     dict                    The dictionary of changes to be made
                @param {Object}     options
                @param {String}     [options.update_mode]   The update mode for this item. Possible values: 'append', 'reset', 'exclude'
                @param {Boolean}    [options.sync]          Determine whether we should sync the data with the server
                @param {Boolean}    [options.silent]        Determine whether we should silently update the model or not
                @param {Object}     [options.filter]        Filter the objects to be modified
            ###
            logger.info "Modifying data from #{channel} in DataSource"
            resource_type = @_getType(channel)

            # Split the channel into its components and get the "id" part.
            item = channels_utils.splitChannel(channel)[1]
            channel_guid = channels_utils.getChannelKey(channel)

            if resource_type == 'relational'
                if item == "all"
                    # Modifying the whole collection is not supported for Backbone collections
                    # Exception is made when a filter is passed in options
                    unless options.filter? or _.isEmpty(options.filter)
                        logger.error("Modifying the whole collection is not supported for
                                  relational collections")
                        return

                # Modify the channel_guid that we received the /modify on, doing sync only
                # for this one, if sync = true...
                @_findAndModifyRelationalChannelModel(channel_guid, item, dict, options)

                # ... Then go through all other channels and update
                # those of the same type with channel_guid containing the item.
                channel_type = @meta_data[channel_guid].type
                for other_channel_guid, other_channel_data of @meta_data
                    # Skip the original channel, we've already modified this one.
                    continue if channel_guid == other_channel_guid
                    if other_channel_data.type == channel_type
                        # Don't sync with server, we already sync'ed above.
                        @_findAndModifyRelationalChannelModel(other_channel_guid, item, dict, _.extend(options, {sync: false}))

            else if resource_type == 'api'
                # For raw data channels, we don't support individual model modifications.
                if item != "all"
                    logger.error("Modifying individual items is not supported for
                                  raw collections")
                    return
                @_modifyApiDataChannel(channel_guid, dict, options.update_mode)

        addToDataChannel: (channel, dict) =>
            ###
                This gets called whenever a new widget publishes to '/add' channel

            ###
            logger.info "Adding new data to #{channel} in DataSource"
            # Get the collection associated with this channel
            collection = channels_utils.getChannelKey(channel)

            # HACK: determine the sync for this item. It is sent in the
            # dict updates ...
            sync = dict['__sync__']
            delete dict['__sync__']

            model = new @data[collection].model(dict)

            # Based on the sync argument we decide whether we should
            # save the model on the server
            if sync

                # Copy the url of the collection to the model, until the model
                # is appended to the collection. Check BaseModel.url()
                #
                # If collection doesn't have an URL, we will take the vanilla URL
                # from the configuration of the channel and check if it needs
                # any parameters. If it doesn't, we will use it. Otherwise,
                # we will raise an error.
                if not @data[collection].url?
                    channel_config = @_getConfig(collection)
                    if not channel_config.url? or channel_config.url.search(/{{[^{}]*}}/) != -1
                        logger.error("Channel #{collection} doesn't have an URL or it needs params")
                        return
                    collection_url = channel_config.url
                else
                    collection_url = @data[collection].url

                model.urlRoot = collection_url

                # Trigger a custom invalidate event before the
                # model is saved to the server. Backbone.Model emits
                # a sync event if the save was successful
                model.trigger('invalidate', model, null)
                # Instead of adding the model to the collection via .create perform
                # a manual save and if the operation is successful then append the
                # model to the collection. By default collection.create appends
                # the model to the collection even if the model wasn't saved
                # successfully (and we don't want that)
                model.save(model.attributes, {
                    error: (model, response, options) =>
                        # Trigger an error event on the collection, even though the model
                        # is not part of the collection yet. This is a CONVENTION to
                        # ease the work with new models
                        @data[collection].trigger('error', model, @data[collection], response)
                    success: (model, response) =>
                        if _.isArray(response)
                            # Sometimes, we make one single POST which
                            # result in multiple items being created. In
                            # this case, the response will be an array
                            # of individual items, and these should be added
                            # to the channel instead of the original POSTed
                            # model.
                            model_class = @meta_data[collection].model_class
                            for response_item in response
                                model = new model_class(response_item)
                                @data[collection].add(model)
                        else if _.isObject(response)
                            # Update model with attributes to sync from response.
                            @syncModelWithResponse(model, response)
                            # Make sure that we propagate ID of object
                            # coming from server to the actual Backbone Model.
                            # Otherwise, the model freshly added in the collection
                            # will not have an ID and we cannot use it immediately.
                            model.set('id', response.id, {silent: true})
                            @data[collection].add(model)
                        else
                            @data[collection].add(model)
                })
            else
                # Just add the model in the collection
                @data[collection].add(model)

        syncModelWithResponse: (model, response, silent = true) ->
            ###
                Given a model and a response, if the
                model has a sync_with_server list,
                look each field in the response and
                overwrite it in the model, if it exists.
            ###
            return unless $.isArray(model?.sync_with_server)

            obj = {}
            for field in model.sync_with_server
                if field of response
                    obj[field] = response[field]
            model.set(obj, { silent: silent })

        _deleteFromRelationalDataChannel: (channel, options) ->
            ###
                Delete a model from a Backbone collection. Calls
                destroy on the model if the change has to be synced with
                the server, otherwise removes the element from the
                collection
            ###
            # Split channel into it's components. Ignoring events
            [collection_name, item, events] = channels_utils.splitChannel(channel)

            collection = @data[channels_utils.formChannel(collection_name)]

            if item is "all"
                # This case will handle the situation when you want
                # to delete from collection by a filter
                unless options.filter? or _.isEmpty(options.filter)
                    logger.error("Deleting whole collection is not supported for
                                  relational collections")
                # All collections should extend base_collection (where filter_by is defined)
                filtered_models = collection.filter_by(options.filter)
            else
                filtered_models = [collection.get(item)]

            for model in filtered_models
                # If the destroy has to be synced with the server
                if options.sync
                    # Destroy the object
                    # http://documentcloud.github.com/backbone/#Model-destroy
                    model?.destroy({ wait: true })
                else
                    # Remove the object from it's collection
                    collection.remove(model)

        deleteFromDataChannel: (channel, options = {sync: true}) =>
            ###
                Delete an item from a channel. You can only delete
                from relational channels

                @param {String}         channel             The channel where objects should be removed
                @param {Object}         options
                @param {Boolean}        [options.sync]      Determine if the deletion should be sent to server
                @param {Object}         [options.filter]    Filter the objects to be deleted
            ###
            logger.info "Deleting data from #{channel} in DataSource"

            channel_type = @_getType(channels_utils.getChannelKey(channel))
            if channel_type == 'relational'
                @_deleteFromRelationalDataChannel(channel, options)
            else if channel_type == 'api'
                logger.error("Deleting from api channels is not supported")



        newWidget: (widget_data) =>
            ###
                This gets called whenever a new widget announces its existence.

                It determines which data from the data source is "interesting"
                for the widget and subscribes the widget to changes on that data.
            ###
            logger.info "Initializing #{widget_data.name} widget in DataSource"

            # For each of the data channels the widget is subscribed to
            for channel, real_channel of widget_data.subscribed_channels
                do (channel, real_channel) =>
                    # Subscribe the widget to the events of the channel
                    @_bindWidgetToChannel(channel, real_channel, widget_data)
                    #add reference counter for determining if this channel
                    #is still in use or not
                    collection = channels_utils.getChannelKey(real_channel)
                    @meta_data[collection]['reference_count'] = (@meta_data[collection]['reference_count'] ? 0) + 1
                    #this timestamp allows us to see for how long the channel
                    #has been inactive
                    @meta_data[collection]['time_of_reference_expiry'] = null

        destroyWidget: (widget_data) =>

            logger.warn "Destroy #{widget_data.name} widget in DataSource"
            for fake_channel, channel of widget_data.widget.channel_mapping
                if not (channel of @meta_data)
                    logger.warn('Could not unbind widget from collection ' +
                                 collection + ' because it was already gone')
                    continue

                # Start unbinding the widget to the existing channel.
                widget_method = @_getWidgetMethod(fake_channel, widget_data.widget)
                [collection, item, events] = channels_utils.splitChannel(fake_channel)

                # For relational channel, we have item-level unbinding and
                # collection-level unbinding, depending on the type of widget
                # subscription.
                if @_getType(channel) == 'relational'
                    if item == "all"
                        @data[channel].off(events, widget_method, widget_data.widget)
                    else
                        individual_item = @data[channel].get(item)
                        # Here we might have a problem: when resetting a
                        # collection, there is no way to keep references to the
                        # old widgets so that we unbind events from them.
                        # TODO(andrei): investigate if we can do something in
                        # the BaseModel class.
                        if individual_item
                            individual_item.off(events, widget_method, widget_data.widget)
                else if @_getType(channel) == 'api'
                    @data[channel].off(events, widget_method, widget_data.widget)

                @meta_data[channel]['reference_count'] -= 1
                if @meta_data[channel]['reference_count'] == 0
                    @meta_data[channel]['time_of_reference_expiry'] = (new Date).getTime()

        checkForUnusedCollections: =>
            ###
                This function gets cleaned up periodically in order to
                inspect which channels still have a non-zero reference count
                and which don't.

                Those who have been inactive (e.g., 0 reference count) for
                quite a while (> checkIntervalForUnusedCollections) will be
                garbage colllected, unless they are eternal.

                Some collections might be eternal, and this is a per-channel
                flag (so not found in datasource.js, but passed to
                Utils.newDataChannels when creating channel instances) because
                for example they are created from the application controller
                and they should live for the whole navigation session regardless
                of whether what is found on the page actually references them
                or not.
            ###
            for collection of @meta_data
                meta = @meta_data[collection]

                # Eternal collections are never expired
                if meta.eternal
                    continue

                # If this collection still has references attached, so skip it.
                if meta['time_of_reference_expiry'] == null
                    continue

                # Channels with pending fetches should not be garbage collected
                if 'waiting_fetches' of meta and meta.waiting_fetches > 0
                    continue

                # Check if the current collection has had
                # 0 reference count for quite a while.
                expired_for = (new Date).getTime() - meta['time_of_reference_expiry']
                if expired_for > @checkIntervalForUnusedCollections
                    # Declare that channel has expired loudly and openly.
                    logger.warn("#{collection} collection expired in DataSource.")
                    # Stop periodic refresh if it was enabled
                    @_stopRefreshing(collection)
                    # Throw away channel meta-data
                    delete @meta_data[collection]
                    # Delete cyclic reference from channel to its buffer
                    if @data[collection].buffer
                        delete @data[collection].buffer.collection
                        @data[collection].buffer.off()
                        delete @data[collection].buffer
                    # Unbind all remaining widgets (should be none!)
                    @data[collection].off()
                    # Throw away reference to the actual data
                    delete @data[collection]

        _checkForNewlyArrivedAndAwaitedModels: (channel) =>
            ###
                Checks if some new models which were awaited for have appeared
                into the given channel. If there are, bind the respective
                widgets to the individual models and drop the widget references.
            ###

            # Check if channel still exists
            if not (channel of @meta_data)
                logger.warn("Channel #{channel} has probably been garbage collected too early")
                return

            # Check if channel has pending items to wait for
            if not ('delayed_single_items' of @meta_data[channel])
                return

            remaining_delayed_items = []
            for delayed_item in @meta_data[channel].delayed_single_items
                single_item = @data[channel].get(delayed_item.id)

                # If the item still hasn't appeared, plan it for later re-use
                if not single_item
                    remaining_delayed_items.push(delayed_item)
                    continue
                # Otherwise, do the binding and drop the widget reference
                else
                    @_bindWidgetToRelationalChannel(delayed_item.fake_channel,
                                                    delayed_item.channel,
                                                    delayed_item.widget_data)

            # Check if there are still single items to wait for
            if remaining_delayed_items.length > 0
                @meta_data[channel].delayed_single_items = remaining_delayed_items
            else
                delete @meta_data[channel]['delayed_single_items']

        _bindWidgetToRelationalChannel: (fake_channel, channel, widget_data) =>
            ###
                Given a widget, bind it to the events of a backbone collection
                or of an individual item of the collection.
            ###

            # Determine the method to be called on the widget
            [collection, item, events] = channels_utils.splitChannel(channel)
            collection = '/' + collection
            widget_method = @_getWidgetMethod(fake_channel, widget_data.widget)
            if not widget_method
                return

            # Whole collection and also give the widget context
            if item == "all"
                @data[collection].on(events, widget_method, widget_data.widget)
                # If data is already there, just pretend it arrived just now.
                # but only if a fetch from server is not in progress
                # otherwise a unwanted list refresh will be triggered
                if @meta_data[collection].last_fetch? and
                (not @meta_data[collection].waiting_fetches? or @meta_data[collection].waiting_fetches is 0)
                    widget_method('reset', @data[collection])
            # Individual collection models
            else
                individual_model = @data[collection].get(item)
                # If model is already there, we just bind it and get over with it
                if individual_model
                    individual_model.on(events, widget_method, widget_data.widget)
                    widget_method('change', individual_model)
                # Else, enqueue the (individual model ID, widget) pair and keep
                # checking for new items whenever data arrives into this channel.
                # When the model finally arrives, drop the reference to the widget.
                else
                    if not ('delayed_single_items' of @meta_data[collection])
                        @meta_data[collection]['delayed_single_items'] = []
                    @meta_data[collection]['delayed_single_items'].push(
                        fake_channel: fake_channel
                        channel: channel
                        widget_data: widget_data
                        id: item
                    )

        _bindWidgetToApiChannel: (fake_channel, channel, widget_data) =>
            ###
                Given a widget, bind it to the events of an api (raw data) channel.
            ###
            [collection, item, events] = channels_utils.splitChannel(channel)
            collection = '/' + collection
            widget_method = @_getWidgetMethod(fake_channel, widget_data.widget)
            if not widget_method
                return

            raw_channel = @data[collection]
            raw_channel.on(events, widget_method, widget_data.widget)

            # If data is already there, just pretend it arrived just now.
            if @meta_data[collection].last_fetch
                widget_method('change', @data[collection])

        _bindWidgetToChannel: (fake_channel, channel, widget_data) =>
            ###
                Bind a widget to a given channel's events.

                This is the __only__ place in which the datalayer should use
                the widget reference. The reason for which we need the reference
                here is that it subscribes it to the events of the private data
                of the datasource.

                This will actually delegate to more specific types of bindings:
                    - bindings of widgets to backbone collections
                        (for relational channels)
                    - bindings of widgets to raw data
                        (for api channels)
            ###
            logger.info "Linking widget #{widget_data.name} to #{channel}"
            resource_type = @_getType(channel)
            if resource_type == 'relational'
                @_bindWidgetToRelationalChannel(fake_channel, channel, widget_data)
            else if resource_type == 'api'
                @_bindWidgetToApiChannel(fake_channel, channel, widget_data)

        pushDataAfterScroll: (channels) =>
            ###
                This gets called every time a widget publishes to "/scroll"

                Data sources receives the scrollable_channels, sets the new collection
                page based on the channels, which will trigger the widget to update
            ###

            # For each of the scrollable channels the widget is subscribed to
            for channel in channels
                do (channel) =>
                    logger.info "Scrolling #{channel} in DataSource"
                    @_fetchChannelDataFromServer(channel, 'scroll')

        pushDataAfterRefresh: (channels, options = {}) =>
            ###
                This gets called every time a widget publishes to "/refresh"

                Data sources will update the data channel according to its
                configured policy.

                Here it can happen a flush channel buffer or a channel refresh
                To skip the buffer flush pass skipStreampollBuffer = true in options param
            ###

            # If channels is an array, it means that we're not receiving any
            # parameters to the channels refresh.
            if $.isArray(channels)
                dict = {}
                for channel in channels
                    # Use existing params if no params were specified
                    dict[channel] = @meta_data[channel].params
            # Otherwise, we're getting channel-specific params for refresh
            else if $.isPlainObject(channels)
                dict = channels
            else
                logger.warn("Unknown parameter type for pushDataAfterRefresh: #{channels}")
                return

            for channel, params of dict
                do (channel, params) =>
                    logger.info "Sends data to #{channel} in DataSource"

                    params_modified = not _.isEqual(@meta_data[channel].params, params)
                    @meta_data[channel].params = params if params_modified

                    # Allow to skip a streampoll buffer flush
                    # By default skip_streampoll_buffer = false
                    skip_streampoll_buffer = if options.skipStreampollBuffer? then options.skipStreampollBuffer else false

                    config_buffer_size = @_getBufferSize(channel)
                    channel_has_buffer = config_buffer_size > 0

                    # Current buffer length is 0 if channel is not configured with a buffer
                    current_buffer_size = if channel_has_buffer then @data[channel].buffer.length else 0

                    # If channel has no buffer that buffer_is_full = true
                    buffer_is_full = current_buffer_size >= config_buffer_size

                    # Refresh channel if these conditions are met:
                    #  - skip_streampoll_buffer = true, or
                    #  - The channel buffer is full, or
                    #  - The channel params were modified
                    if skip_streampoll_buffer or buffer_is_full or params_modified
                        # If we have to do a fresh fetch from the server,
                        # empty the existing buffer first
                        @data[channel].buffer.reset([]) if channel_has_buffer
                        @_fetchChannelDataFromServer(channel)
                        @_restartRefreshing(channel)
                    else
                        @_flushChannelBuffer(channel)

        _channelHasFixture: (name) ->
            ###
                Check if channel has a fixture
            ###
            base_type = @meta_data[name].type
            return base_type[1..] of Fixtures

        _fixtureMatchesParams: (item, params) ->
            ###
                Determines if a fixture item matches the given parameters:
                 * {gender: 'm'} => item.gender == 'm'
            ###
            for k, v of params
                if not k of item
                    return false
                if item[k] != v
                    return false

            return true

        _loadFixtures: (channel = null, params = {}, id_offset=0, add_instead_of_push=false) =>
            ###
                Loads fixtures from the fixtures.js file.

                This will initialize the proper collections and populate them with data.
            ###

            # Determine which collections to load - those found in the
            # configuration and also found in the Fixtures array.
            collections_to_load = []

            if channel
                if @_channelHasFixture(channel)
                    collections_to_load = [channel]
            else
                collections_to_load = [name for name of @data when @_chanelHasFixture(name)]

            for name in collections_to_load
                base_type = @meta_data[name].type
                model_fixtures = Fixtures[base_type[1..]].responseText
                collection_instance = @data[name]

                resource_type = @_getType(name)
                if resource_type == 'relational'
                    added = 0
                    for fixture_item in model_fixtures
                        fixture_item.id += id_offset
                        # Check if the fixtured item matches the given parameters
                        if @_fixtureMatchesParams(fixture_item, params)
                            added = added + 1
                            model = new collection_instance.model(fixture_item)
                            if add_instead_of_push
                                collection_instance.add(model)
                            else
                                collection_instance.push(model)
                    logger.info("Added #{added} fixtured items to channel #{name}")
                else if resource_type == 'api'
                    collection_instance.data = model_fixtures
                    logger.info("Added fixtures to channel #{name}")

        destroy: ->
            logger.info "Destroying data source"

    return DataSource
