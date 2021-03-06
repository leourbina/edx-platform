/**
 * XBlockEditorView displays the authoring view of an xblock, and allows the user to switch between
 * the available modes.
 */
define(["jquery", "underscore", "gettext", "js/views/feedback_notification", "js/views/xblock",
        "js/views/metadata", "js/collections/metadata", "jquery.inputnumber"],
    function ($, _, gettext, NotificationView, XBlockView, MetadataView, MetadataCollection) {

        var XBlockEditorView = XBlockView.extend({
            // takes XBlockInfo as a model

            options: $.extend({}, XBlockView.prototype.options, {
                view: 'studio_view'
            }),

            initialize: function() {
                XBlockView.prototype.initialize.call(this);
                this.view = this.options.view;
            },

            xblockReady: function(xblock) {
                XBlockView.prototype.xblockReady.call(this, xblock);
                this.initializeEditors();
            },

            initializeEditors: function() {
                var metadataEditor,
                    defaultMode = 'editor';
                metadataEditor = this.createMetadataEditor();
                this.metadataEditor = metadataEditor;
                if (!this.hasCustomTabs()) {
                    if (this.getDataEditor()) {
                        defaultMode = 'editor';
                    } else if (metadataEditor) {
                        defaultMode = 'settings';
                    }
                    this.selectMode(defaultMode);
                }
            },

            getDefaultModes: function() {
                return [
                    { id: 'editor', name: gettext("Editor")},
                    { id: 'settings', name: gettext("Settings")}
                ];
            },

            hasCustomTabs: function() {
                return this.$('.editor-with-tabs').length > 0;
            },

            hasCustomButtons: function() {
                return this.$('.editor-with-buttons').length > 0;
            },

            createMetadataEditor: function() {
                var metadataEditor,
                    metadataData,
                    models = [],
                    key,
                    xblock = this.xblock,
                    metadataView = null;
                metadataEditor = this.$('.metadata_edit');
                if (metadataEditor.length === 1) {
                    metadataData = metadataEditor.data('metadata');
                    for (key in metadataData) {
                        if (metadataData.hasOwnProperty(key)) {
                            models.push(metadataData[key]);
                        }
                    }
                    metadataView = new MetadataView.Editor({
                        el: metadataEditor,
                        collection: new MetadataCollection(models)
                    });
                    if (xblock.setMetadataEditor) {
                        xblock.setMetadataEditor(metadataView);
                    }
                }
                return metadataView;
            },

            getDataEditor: function() {
                var editor = this.$('.wrapper-comp-editor');
                return editor.length === 1 ? editor : null;
            },

            getMetadataEditor: function() {
                return this.metadataEditor;
            },

            save: function(options) {
                var xblockInfo = this.model,
                    data,
                    saving;
                data = this.getXModuleData();
                if (data) {
                    saving = new NotificationView.Mini({
                        title: gettext('Saving&hellip;')
                    });
                    saving.show();
                    return xblockInfo.save(data).done(function() {
                        var success = options.success;
                        saving.hide();
                        if (success) {
                            success();
                        }
                    });
                }
            },

            /**
             * Returns the data saved for the xmodule. Note that this *does not* work for XBlocks.
             */
            getXModuleData: function() {
                var xblock = this.xblock,
                    metadataEditor = this.getMetadataEditor(),
                    data = null;
                if (xblock.save) {
                    data = xblock.save();
                    if (metadataEditor) {
                        data.metadata = _.extend(data.metadata || {}, this.getChangedMetadata());
                    }
                } else {
                    console.error('Cannot save xblock as it has no save method');
                }
                return data;
            },

            /**
             * Returns the metadata that has changed in the editor. This is a combination of the metadata
             * modified in the "Settings" editor, as well as any custom metadata provided by the component.
             */
            getChangedMetadata: function() {
                var metadataEditor = this.getMetadataEditor();
                return _.extend(metadataEditor.getModifiedMetadataValues(), this.getCustomMetadata());
            },

            /**
             * Returns custom metadata defined by a particular xmodule that aren't part of the metadata editor.
             * In particular, this is used for LaTeX high level source.
             */
            getCustomMetadata: function() {
                // Walk through the set of elements which have the 'data-metadata_name' attribute and
                // build up an object to pass back to the server on the subsequent POST.
                // Note that these values will always be sent back on POST, even if they did not actually change.
                var metadata, metadataNameElements, i, element, metadataName;
                metadata = {};
                metadataNameElements = this.$('[data-metadata-name]');
                for (i = 0; i < metadataNameElements.length; i++) {
                    element = metadataNameElements[i];
                    metadataName = $(element).data("metadata-name");
                    metadata[metadataName] = element.value;
                }
                return metadata;
            },

            getMode: function() {
                return this.mode;
            },

            selectMode: function(mode) {
                var showEditor = mode === 'editor',
                    dataEditor = this.getDataEditor(),
                    metadataEditor = this.getMetadataEditor();
                if (dataEditor) {
                    this.setEditorActivation(dataEditor, showEditor);
                }
                if (metadataEditor) {
                    this.setEditorActivation(metadataEditor.$el, !showEditor);
                }
                this.mode = mode;
            },

            setEditorActivation: function(editor, isActive) {
                editor.removeClass('is-active').removeClass('is-inactive');
                editor.addClass(isActive ? 'is-active' : 'is-inactive');
            }
        });

        return XBlockEditorView;
    }); // end define();
