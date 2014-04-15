# -*- coding: utf-8 -*-

"""
Acceptance tests for Video.
"""

from .helpers import UniqueCourseTest
from ..pages.lms.video import VideoPage
from ..pages.lms.tab_nav import TabNavPage
from ..pages.lms.course_nav import CourseNavPage
from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.lms.course_info import CourseInfoPage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc

VIDEO_SOURCE_PORT = 8777

HTML5_SOURCES = [
    'http://localhost:{0}/gizmo.mp4'.format(VIDEO_SOURCE_PORT),
    'http://localhost:{0}/gizmo.webm'.format(VIDEO_SOURCE_PORT),
    'http://localhost:{0}/gizmo.ogv'.format(VIDEO_SOURCE_PORT),
]

HTML5_SOURCES_INCORRECT = [
    'http://localhost:{0}/gizmo.mp99'.format(VIDEO_SOURCE_PORT),
]


class VideoBaseTest(UniqueCourseTest):
    """
    Base class for tests of the Video Player
    Sets up the course and provides helper functions for the Video tests.
    """

    def setUp(self):
        """
        Initialization of pages and course fixture for video tests
        """
        super(VideoBaseTest, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        self.course_fixture = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        self.metadata = None
        self.assets = []
        self.verticals = None

    def navigate_to_video(self):
        """ Prepare the course and get to the video and render it """
        self._install_course_fixture()
        self._navigate_to_courseware_video_and_render()

    def navigate_to_video_no_render(self):
        """
        Prepare the course and get to the video unit
        however do not wait for it to render, because
        the has been an error.
        """
        self._install_course_fixture()
        self._navigate_to_courseware_video_no_render()

    def _install_course_fixture(self):
        """ Install the course fixture that has been defined """
        if self.assets:
            self.course_fixture.add_asset(self.assets)

        chapter_sequential = XBlockFixtureDesc('sequential', 'Test Section')
        chapter_sequential.add_children(*self._add_course_verticals())
        chapter = XBlockFixtureDesc('chapter', 'Test Chapter').add_children(chapter_sequential)
        self.course_fixture.add_children(chapter)
        self.course_fixture.install()

    def _add_course_verticals(self):
        """
        Create XBlockFixtureDesc verticals
        :return: a list of XBlockFixtureDesc
        """
        xblock_verticals = []
        _verticals = self.verticals

        # there must be at-least single vertical with a single video
        if not _verticals:
            _verticals = [[{'display_name': 'Video', 'metadata': self.metadata}]]

        for vertical_index, vertical in enumerate(_verticals):
            xblock_verticals.append(self._create_single_vertical(vertical, vertical_index))

        return xblock_verticals

    def _create_single_vertical(self, vertical, vertical_index):
        """
        Create a single course vertical of type XBlockFixtureDesc with category `vertical`, a single course vertical
        can contain single or multiple video modules
        :param vertical: vertical data list
        :param vertical_index: index for the vertical display name
        :return: XBlockFixtureDesc
        """
        xblock_course_vertical = XBlockFixtureDesc('vertical', 'Test Vertical-{0}'.format(vertical_index))

        for video in vertical:
            xblock_course_vertical.add_children(
                XBlockFixtureDesc('video', video['display_name'], metadata=video.get('metadata')))

        return xblock_course_vertical

    def _navigate_to_courseware_video(self):
        """ Register for the course and navigate to the video unit """
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

    def _navigate_to_courseware_video_and_render(self):
        """ Wait for the video player to render """
        self._navigate_to_courseware_video()
        self.video.wait_for_video_player_render()

    def _navigate_to_courseware_video_no_render(self):
        """ Wait for the video Xmodule but not for rendering """
        self._navigate_to_courseware_video()
        self.video.wait_for_video_class()

    def get_metadata(self, player_mode, data=None):
        """
        Create a dictionary for video player configuration according to `player_mode`
        :param player_mode (str): Video player mode
        :param data (dict): Video metadata values
        :return: dict
        """
        metadata = {}

        if player_mode == 'html5':
            metadata.update({
                'youtube_id_1_0': '',
                'youtube_id_0_75': '',
                'youtube_id_1_25': '',
                'youtube_id_1_5': '',
                'html5_sources': HTML5_SOURCES
            })

        if player_mode == 'youtube_html5':
            metadata.update({
                'html5_sources': HTML5_SOURCES,
            })

        if player_mode == 'youtube_html5_unsupported_video':
            metadata.update({
                'html5_sources': HTML5_SOURCES_INCORRECT
            })

        if player_mode == 'html5_unsupported_video':
            metadata.update({
                'youtube_id_1_0': '',
                'youtube_id_0_75': '',
                'youtube_id_1_25': '',
                'youtube_id_1_5': '',
                'html5_sources': HTML5_SOURCES_INCORRECT
            })

        # if player_mode == 'flash':
        #     metadata.update(FLASH_SOURCES)
        #     world.browser.cookies.add({'edX_video_player_mode': 'flash'})

        if data:
            metadata.update(data)

        return metadata

    def open_video(self, video_display_name):
        """
        Navigate to sequential specified by `video_display_name`
        :param video_display_name (str): Sequential Title
        """
        self.course_nav.go_to_sequential(video_display_name)
        self.video.wait_for_video_player_render()


class YouTubeVideoTest(VideoBaseTest):
    """ Test YouTube Video Player """

    def setUp(self):
        super(YouTubeVideoTest, self).setUp()

    def test_video_component_rendered_in_youtube_without_html5_sources(self):
        """
        Scenario: Video component is rendered in the LMS in Youtube mode without HTML5 sources
        Given the course has a Video component in "Youtube" mode
        Then the video has rendered in "Youtube" mode
        """
        self.navigate_to_video()

        # Verify that video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

    def test_cc_button_without_english_transcript_youtube_mode(self):
        """
        Scenario: CC button works correctly w/o english transcript in Youtube mode of Video component
        Given the course has a Video component in "Youtube" mode
        And I have defined a non-english transcript for the video
        And I have uploaded a non-english transcript file to assets
        Then I see the correct text in the captions
        """
        data = {'transcripts': {'zh': 'chinese_transcripts.srt'}}
        self.metadata = self.get_metadata('youtube', data)
        self.assets.append('chinese_transcripts.srt')
        self.navigate_to_video()
        self.video.show_captions()

        # Verify that we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)

    def test_cc_button_transcripts_and_sub_fields_empty(self):
        """
        Scenario: CC button works correctly if transcripts and sub fields are empty,
        but transcript file exists in assets (Youtube mode of Video component)
        Given the course has a Video component in "Youtube" mode
        And I have uploaded a .srt.sjson file to assets
        Then I see the correct english text in the captions
        """
        self.assets.append('subs_OEoXaMPEzfM.srt.sjson')
        self.navigate_to_video()
        self.video.show_captions()

        # Verify that we see "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)

    def test_cc_button_hidden_if_no_translations(self):
        """
        Scenario: CC button is hidden if no translations
        Given the course has a Video component in "Youtube" mode
        Then the "CC" button is hidden
        """
        self.navigate_to_video()
        self.assertFalse(self.video.is_button_shown('CC'))

    def test_video_aligned_correctly_if_transcript_hidden_in_full_screen(self):
        """
        Scenario: Video is aligned correctly if transcript is hidden in fullscreen mode
        Given the course has a Video component in "Youtube" mode
        """
        self.navigate_to_video()

        # click video button "fullscreen"
        self.video.click_player_button('fullscreen')

        # check if video aligned correctly without enabled transcript
        self.assertTrue(self.video.is_aligned(False))

    def test_download_button_works_correctly_without_english_transcript_youtube_mode(self):
        """
        Scenario: Download button works correctly w/o english transcript in Youtube mode of Video component
        Given
            I have a "chinese_transcripts.srt" transcript file in assets
            And it has a video in "Youtube" mode
        """
        data = {'download_track': True, 'transcripts': {'zh': 'chinese_transcripts.srt'}}
        self.metadata = self.get_metadata('youtube', data=data)
        self.assets.append('chinese_transcripts.srt')

        # go to video
        self.navigate_to_video()

        # check if we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)

        # check if we can download transcript in "srt" format that has text "好 各位同学"
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertTrue(self.video.can_we_download_transcript('srt', unicode_text))

    def test_download_button_works_correctly_non_english_transcript_youtube_mode(self):
        """
        Scenario: Download button works correctly for non-english transcript in Youtube mode of Video component
        Given
            I have a "chinese_transcripts.srt" transcript file in assets
            And I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets
            And it has a video in "Youtube" mode
        """
        self.assets.extend(['chinese_transcripts.srt', 'subs_OEoXaMPEzfM.srt.sjson'])
        data = {'download_track': True, 'transcripts': {'zh': 'chinese_transcripts.srt'}, 'sub': 'OEoXaMPEzfM'}
        self.metadata = self.get_metadata('youtube', data=data)

        # go to video
        self.navigate_to_video()

        # check if "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)

        # check if we can download transcript in "srt" format that has text "Hi, welcome to Edx."
        self.assertTrue(self.video.can_we_download_transcript('srt', 'Hi, welcome to Edx.'))

        # select language with code "zh"
        self.assertTrue(self.video.select_language('zh'))

        # check if we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)

        # check if we can download transcript in "srt" format that has text "好 各位同学"
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertTrue(self.video.can_we_download_transcript('srt', unicode_text))

    def test_video_aligned_correctly_on_transcript_toggle_in_fullscreen(self):
        """
        Tests that Video is aligned correctly on transcript toggle in fullscreen mode Given I have a
        "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets And it has a video in "Youtube" mode.
        """
        self.assets.append('subs_OEoXaMPEzfM.srt.sjson')
        data = {'sub': 'OEoXaMPEzfM'}
        self.metadata = self.get_metadata('youtube', data=data)

        # go to video
        self.navigate_to_video()

        # make sure captions are opened
        self.video.show_captions()

        # click video button "fullscreen"
        self.video.click_player_button('fullscreen')

        # check if video aligned correctly with enabled transcript
        self.assertTrue(self.video.is_aligned(True))

        # click video button "CC"
        self.video.click_player_button('CC')

        # check if video aligned correctly without enabled transcript
        self.assertTrue(self.video.is_aligned(False))


class YouTubeHtml5VideoTest(VideoBaseTest):
    """ Test YouTube HTML5 Video Player """

    def setUp(self):
        super(YouTubeHtml5VideoTest, self).setUp()

    def test_video_component_rendered_in_youtube_with_unsupported_html5_sources(self):
        """
        Scenario: Video component is rendered in the LMS in Youtube mode
                  with HTML5 sources that doesn't supported by browser
        Given the course has a Video component in "Youtube_HTML5_Unsupported_Video" mode
        Then the video has rendered in "Youtube" mode
        """
        self.metadata = self.get_metadata('youtube_html5_unsupported_video')
        self.navigate_to_video()

        # Verify that the video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

    def test_multiple_videos_in_sequentials_load_and_work(self):
        """
        Scenario: Multiple videos in sequentials all load and work, switching between sequentials
        Given
            And it has a video "A" in "Youtube" mode in position "1" of sequential
            And a video "B" in "HTML5" mode in position "1" of sequential
            And a video "C" in "Youtube" mode in position "1" of sequential
            And a video "D" in "Youtube" mode in position "1" of sequential
            And a video "E" in "Youtube" mode in position "2" of sequential
            And a video "F" in "Youtube" mode in position "2" of sequential
            And a video "G" in "Youtube" mode in position "2" of sequential
        """

        self.verticals = [
            [{'display_name': 'A'}, {'display_name': 'B', 'metadata': self.get_metadata('html5')},
             {'display_name': 'C'}, {'display_name': 'D'}],
            [{'display_name': 'E'}], [{'display_name': 'F'}]
        ]

        # go to video
        self.navigate_to_video()

        # check if video "A" should start playing at speed "1.0"
        self.assertEqual(self.video.speed, '1.0x')

        # select the "2.0" speed on video "B"
        self.open_video('B')
        self.video.speed = '2.0'

        # select the "2.0" speed on video "C"
        self.open_video('C')
        self.video.speed = '2.0'

        # select the "2.0" speed on video "D"
        self.open_video('D')
        self.video.speed = '2.0'

        # open video "E"
        self.open_video('E')

        # check if video "E" should start playing at speed "2.0"
        self.assertEqual(self.video.speed, '2.0x')

        # select the "1.0" speed on video "F"
        self.open_video('F')
        self.video.speed = '1.0'

        # select the "1.0" speed on video "G"
        self.open_video('G')
        self.video.speed = '1.0'

        # open video "A"
        self.open_video('A')

        # check if video "A" should start playing at speed "2.0"
        self.assertEqual(self.video.speed, '2.0x')


class Html5VideoTest(VideoBaseTest):
    """ Test HTML5 Video Player """

    def setUp(self):
        super(Html5VideoTest, self).setUp()

    def test_autoplay_disabled_for_video_component(self):
        """
        Scenario: Autoplay is disabled in LMS for a Video component
        Given the course has a Video component in "HTML5" mode
        Then it does not have autoplay enabled
        """
        self.metadata = self.get_metadata('html5')
        self.navigate_to_video()

        # Verify that the video has autoplay mode disabled
        self.assertFalse(self.video.is_autoplay_enabled)

    def test_video_component_rendered_in_html5_with_unsupported_html5_sources(self):
        """
        Scenario: Video component is rendered in the LMS in HTML5 mode with HTML5 sources that doesn't
                  supported by browser
        Given the course has a Video component in "HTML5_Unsupported_Video" mode
        Then error message is shown
        And error message has correct text
        """
        self.metadata = self.get_metadata('html5_unsupported_video')
        self.navigate_to_video_no_render()

        # Verify that error message is shown
        self.assertTrue(self.video.is_error_message_shown)

        # Verify that error message has correct text
        correct_error_message_text = 'ERROR: No playable video sources found!'
        self.assertIn(correct_error_message_text, self.video.error_message_text)

    def test_download_button_works_correctly_without_english_transcript_html5_mode(self):
        """
        Scenario: Download button works correctly w/o english transcript in HTML5 mode of Video component
        Given
            I have a "chinese_transcripts.srt" transcript file in assets
            And it has a video in "HTML5" mode
        """
        data = {'download_track': True, 'transcripts': {'zh': 'chinese_transcripts.srt'}}
        self.metadata = self.get_metadata('html5', data=data)
        self.assets.append('chinese_transcripts.srt')

        # go to video
        self.navigate_to_video()

        # check if we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)

        # check if we can download transcript in "srt" format that has text "好 各位同学"
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertTrue(self.video.can_we_download_transcript('srt', unicode_text))

    def test_download_button_works_correctly_non_english_transcript_html5_mode(self):
        """
        Scenario: Download button works correctly for non-english transcript in HTML5 mode of Video component
        Given
            I have a "chinese_transcripts.srt" transcript file in assets
            And I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets
            And it has a video in "HTML5" mode
        """
        self.assets.extend(['chinese_transcripts.srt', 'subs_OEoXaMPEzfM.srt.sjson'])
        data = {'download_track': True, 'transcripts': {'zh': 'chinese_transcripts.srt'}, 'sub': 'OEoXaMPEzfM'}
        self.metadata = self.get_metadata('html5', data=data)

        # go to video
        self.navigate_to_video()

        # check if "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)

        # check if we can download transcript in "srt" format that has text "Hi, welcome to Edx."
        self.assertTrue(self.video.can_we_download_transcript('srt', 'Hi, welcome to Edx.'))

        # select language with code "zh"
        self.assertTrue(self.video.select_language('zh'))

        # check if we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')

        self.assertIn(unicode_text, self.video.captions_text)

        #Then I can download transcript in "srt" format that has text "好 各位同学"
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertTrue(self.video.can_we_download_transcript('srt', unicode_text))

    def test_video_aligned_correctly_if_transcript_visible_in_full_screen(self):
        """
        Scenario: Video is aligned correctly if transcript is visible in fullscreen mode
        Given
            I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets
            And it has a video in "HTML5" mode
        """
        self.assets.append('subs_OEoXaMPEzfM.srt.sjson')
        data = {'sub': 'OEoXaMPEzfM'}
        self.metadata = self.get_metadata('html5', data=data)

        # go to video
        self.navigate_to_video()

        # make sure captions are opened
        self.video.show_captions()

        # click video button "fullscreen"
        self.video.click_player_button('fullscreen')

        # check if video aligned correctly with enabled transcript
        self.assertTrue(self.video.is_aligned(True))

    def test_cc_button_works_correctly_only_with_english_transcript(self):
        """
        Scenario: CC button works correctly only w/ english transcript in HTML5 mode of Video component
        Given
            I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets
            And it has a video in "HTML5" mode
        """
        self.assets.append('subs_OEoXaMPEzfM.srt.sjson')
        data = {'sub': 'OEoXaMPEzfM'}
        self.metadata = self.get_metadata('html5', data=data)

        # go to video
        self.navigate_to_video()

        # make sure captions are opened
        self.video.show_captions()

        # check if we see "Hi, welcome to Edx." text in the captions
        self.assertIn("Hi, welcome to Edx.", self.video.captions_text)

    def test_cc_button_works_correctly_without_english_transcript_html5_mode(self):
        """
        Scenario: CC button works correctly w/o english transcript in HTML5 mode of Video component
        Given
            I have a "chinese_transcripts.srt" transcript file in assets
            And it has a video in "HTML5" mode
        """
        self.assets.append('chinese_transcripts.srt')
        data = {'transcripts': {'zh': 'chinese_transcripts.srt'}}
        self.metadata = self.get_metadata('html5', data=data)

        # go to video
        self.navigate_to_video()

        # make sure captions are opened
        self.video.show_captions()

        # check if we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)
