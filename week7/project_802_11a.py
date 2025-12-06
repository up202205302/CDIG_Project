#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: CDIG - 802.11a/g/p RX
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
from gnuradio import iio
import foo
import ieee802_11
import sip
import threading



class project_802_11a(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "CDIG - 802.11a/g/p RX", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("CDIG - 802.11a/g/p RX")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "project_802_11a")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.window_size = window_size = 48
        self.update_time = update_time = 1
        self.threshold = threshold = 0.56
        self.samp_rate = samp_rate = 20000000
        self.gain = gain = 20
        self.LO_freq = LO_freq = 2412000000

        ##################################################
        # Blocks
        ##################################################

        # Create the options list
        self._update_time_options = [1, 0.1, 0.01]
        # Create the labels list
        self._update_time_labels = ['1s', '100ms', '10ms']
        # Create the combo box
        self._update_time_tool_bar = Qt.QToolBar(self)
        self._update_time_tool_bar.addWidget(Qt.QLabel("updt" + ": "))
        self._update_time_combo_box = Qt.QComboBox()
        self._update_time_tool_bar.addWidget(self._update_time_combo_box)
        for _label in self._update_time_labels: self._update_time_combo_box.addItem(_label)
        self._update_time_callback = lambda i: Qt.QMetaObject.invokeMethod(self._update_time_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._update_time_options.index(i)))
        self._update_time_callback(self.update_time)
        self._update_time_combo_box.currentIndexChanged.connect(
            lambda i: self.set_update_time(self._update_time_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._update_time_tool_bar)
        self._threshold_range = qtgui.Range(0, 1, 0.01, 0.56, 50)
        self._threshold_win = qtgui.RangeWidget(self._threshold_range, self.set_threshold, "sync_short_threshold", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._threshold_win)
        # Create the options list
        self._samp_rate_options = [20000000, 10000000]
        # Create the labels list
        self._samp_rate_labels = ['20MHz', '10MHz']
        # Create the combo box
        # Create the radio buttons
        self._samp_rate_group_box = Qt.QGroupBox("sampling_rate" + ": ")
        self._samp_rate_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._samp_rate_button_group = variable_chooser_button_group()
        self._samp_rate_group_box.setLayout(self._samp_rate_box)
        for i, _label in enumerate(self._samp_rate_labels):
            radio_button = Qt.QRadioButton(_label)
            self._samp_rate_box.addWidget(radio_button)
            self._samp_rate_button_group.addButton(radio_button, i)
        self._samp_rate_callback = lambda i: Qt.QMetaObject.invokeMethod(self._samp_rate_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._samp_rate_options.index(i)))
        self._samp_rate_callback(self.samp_rate)
        self._samp_rate_button_group.buttonClicked[int].connect(
            lambda i: self.set_samp_rate(self._samp_rate_options[i]))
        self.top_layout.addWidget(self._samp_rate_group_box)
        self._gain_range = qtgui.Range(0, 70, 1, 20, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "sdr_gain", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
        # Create the options list
        self._LO_freq_options = [2412000000, 2417000000, 2422000000, 2427000000, 2432000000, 2437000000, 2442000000, 2447000000, 2452000000, 2457000000, 2462000000, 2467000000, 2472000000, 5180000000, 5200000000, 5220000000, 5240000000, 5260000000, 5280000000, 5300000000, 5320000000, 5500000000, 5520000000, 5540000000, 5560000000, 5580000000, 5600000000, 5620000000, 5640000000, 5660000000, 5680000000, 5700000000, 5720000000, 5745000000, 5765000000, 5785000000, 5805000000, 5825000000, 5860000000, 5870000000, 5875000000, 5880000000, 5885000000, 5890000000, 5895000000, 5900000000, 5905000000, 5910000000, 5920000000]
        # Create the labels list
        self._LO_freq_labels = ['Channel 1   | 802.11g | 2.412GHz', 'Channel 2   | 802.11g | 2.417GHz', 'Channel 3   | 802.11g | 2.422GHz', 'Channel 4   | 802.11g | 2.427GHz', 'Channel 5   | 802.11g | 2.432GHz', 'Channel 6   | 802.11g | 2.437GHz', 'Channel 7   | 802.11g | 2.442GHz', 'Channel 8   | 802.11g | 2.447GHz', 'Channel 9   | 802.11g | 2.452GHz', 'Channel 10| 802.11g | 2.457GHz', 'Channel 11| 802.11g | 2.462GHz', 'Channel 12| 802.11g | 2.467GHz', 'Channel 13| 802.11g | 2.472GHz', 'Channel 36| 802.11a | 5.180GHz', 'Channel 40| 802.11a | 5.200GHz', 'Channel 44| 802.11a | 5.220GHz', 'Channel 48| 802.11a | 5.240GHz', 'Channel 52| 802.11a | 5.260GHz', 'Channel 56| 802.11a | 5.280GHz', 'Channel 60| 802.11a | 5.300GHz', 'Channel 64| 802.11a | 5.320GHz', 'Channel 100| 802.11a | 5.500GHz', 'Channel 104| 802.11a | 5.520GHz', 'Channel 108| 802.11a | 5.540GHz', 'Channel 112| 802.11a | 5.560GHz', 'Channel 116| 802.11a | 5.580GHz', 'Channel 120| 802.11a | 5.600GHz', 'Channel 124| 802.11a | 5.620GHz', 'Channel 128| 802.11a | 5.640GHz', 'Channel 132| 802.11a | 5.660GHz', 'Channel 136| 802.11a | 5.680GHz', 'Channel 140| 802.11a | 5.700GHz', 'Channel 144| 802.11a | 5.720GHz', 'Channel 149| 802.11a | 5.745GHz', 'Channel 153| 802.11a | 5.765GHz', 'Channel 157| 802.11a | 5.785GHz', 'Channel 161| 802.11a | 5.805GHz', 'Channel 165| 802.11a | 5.825GHz', 'Channel 172| 802.11p | 5.860GHz', 'Channel 174| 802.11p | 5.870GHz', 'Channel 175| 802.11p | 5.875GHz', 'Channel 176| 802.11p | 5.880GHz', 'Channel 177| 802.11p | 5.885GHz', 'Channel 178| 802.11p | 5.890GHz', 'Channel 179| 802.11p | 5.895GHz', 'Channel 180| 802.11p | 5.900GHz', 'Channel 181| 802.11p | 5.905GHz', 'Channel 182| 802.11p | 5.910GHz', 'Channel 184| 802.11p | 5.920GHz']
        # Create the combo box
        self._LO_freq_tool_bar = Qt.QToolBar(self)
        self._LO_freq_tool_bar.addWidget(Qt.QLabel("'LO_freq'" + ": "))
        self._LO_freq_combo_box = Qt.QComboBox()
        self._LO_freq_tool_bar.addWidget(self._LO_freq_combo_box)
        for _label in self._LO_freq_labels: self._LO_freq_combo_box.addItem(_label)
        self._LO_freq_callback = lambda i: Qt.QMetaObject.invokeMethod(self._LO_freq_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._LO_freq_options.index(i)))
        self._LO_freq_callback(self.LO_freq)
        self._LO_freq_combo_box.currentIndexChanged.connect(
            lambda i: self.set_LO_freq(self._LO_freq_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._LO_freq_tool_bar)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            512, #size
            1, #samp_rate
            'Autocorrelation Samples', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 10)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.8, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_sink_x_0_0_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            LO_freq, #fc
            samp_rate, #bw
            "Input", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0_0_0.set_update_time(1.0/update_time)
        self._qtgui_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_sink_x_0_0_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0_0_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_0_0_win)
        self.qtgui_sink_x_0_0 = qtgui.sink_f(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            LO_freq, #fc
            samp_rate, #bw
            "Sync Short - Output", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0_0.set_update_time(1.0/update_time)
        self._qtgui_sink_x_0_0_win = sip.wrapinstance(self.qtgui_sink_x_0_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_0_win)
        self.qtgui_sink_x_0 = qtgui.sink_f(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            LO_freq, #fc
            samp_rate, #bw
            "Sync Long - Output", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/update_time)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.qtgui_const_sink_x_0_0 = qtgui.const_sink_c(
            1024, #size
            'Pre-Equalizer', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0_0.enable_grid(False)
        self.qtgui_const_sink_x_0_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            'Post-Equalizer', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.complex_t, 'packet_len')
        self.iio_pluto_source_0_0 = iio.fmcomms2_source_fc32('192.168.2.1' if '192.168.2.1' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0_0.set_frequency(LO_freq)
        self.iio_pluto_source_0_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0_0.set_gain(0, gain)
        self.iio_pluto_source_0_0.set_quadrature(True)
        self.iio_pluto_source_0_0.set_rfdc(True)
        self.iio_pluto_source_0_0.set_bbdc(True)
        self.iio_pluto_source_0_0.set_filter_params('Auto', '', 0, 0)
        self.ieee802_11_sync_short_0 = ieee802_11.sync_short(threshold, 2, False, False)
        self.ieee802_11_sync_long_0 = ieee802_11.sync_long(240, False, False)
        self.ieee802_11_parse_mac_0 = ieee802_11.parse_mac(True, False)
        self.ieee802_11_frame_equalizer_0 = ieee802_11.frame_equalizer(ieee802_11.LS, LO_freq, samp_rate, False, False)
        self.ieee802_11_decode_mac_0 = ieee802_11.decode_mac(True, False)
        self.foo_wireshark_connector_0 = foo.wireshark_connector(127, False)
        self.fir_filter_xxx_0_0 = filter.fir_filter_fff(1, [1]*window_size)
        self.fir_filter_xxx_0_0.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_ccc(1, [1]*window_size)
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.fft_vxx_0 = fft.fft_vcc(64, True, window.rectangular(64), True, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, 64)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, 64)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/home/joao/Documents/feup/masters/1st/1sem/cdig/project/project_git/week7/wifi.pcap', False)
        self.blocks_file_sink_0.set_unbuffered(True)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, 240)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, 16)
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_1_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_1 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.ieee802_11_decode_mac_0, 'out'), (self.ieee802_11_parse_mac_0, 'in'))
        self.msg_connect((self.ieee802_11_frame_equalizer_0, 'symbols'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.ieee802_11_parse_mac_0, 'out'), (self.foo_wireshark_connector_0, 'in'))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_1, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_1_0, 0), (self.qtgui_sink_x_0_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.fir_filter_xxx_0_0, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.ieee802_11_sync_short_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.ieee802_11_sync_long_0, 1))
        self.connect((self.blocks_divide_xx_0, 0), (self.ieee802_11_sync_short_0, 2))
        self.connect((self.blocks_multiply_xx_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_const_sink_x_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.ieee802_11_frame_equalizer_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.ieee802_11_sync_short_0, 1))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.foo_wireshark_connector_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.ieee802_11_frame_equalizer_0, 0), (self.ieee802_11_decode_mac_0, 0))
        self.connect((self.ieee802_11_sync_long_0, 0), (self.blocks_complex_to_mag_1, 0))
        self.connect((self.ieee802_11_sync_long_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.ieee802_11_sync_short_0, 0), (self.blocks_complex_to_mag_1_0, 0))
        self.connect((self.ieee802_11_sync_short_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.ieee802_11_sync_short_0, 0), (self.ieee802_11_sync_long_0, 0))
        self.connect((self.iio_pluto_source_0_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.iio_pluto_source_0_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.iio_pluto_source_0_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.iio_pluto_source_0_0, 0), (self.qtgui_sink_x_0_0_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.qtgui_const_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "project_802_11a")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_window_size(self):
        return self.window_size

    def set_window_size(self, window_size):
        self.window_size = window_size
        self.fir_filter_xxx_0.set_taps([1]*self.window_size)
        self.fir_filter_xxx_0_0.set_taps([1]*self.window_size)

    def get_update_time(self):
        return self.update_time

    def set_update_time(self, update_time):
        self.update_time = update_time
        self._update_time_callback(self.update_time)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self._samp_rate_callback(self.samp_rate)
        self.ieee802_11_frame_equalizer_0.set_bandwidth(self.samp_rate)
        self.iio_pluto_source_0_0.set_samplerate(self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(self.LO_freq, self.samp_rate)
        self.qtgui_sink_x_0_0.set_frequency_range(self.LO_freq, self.samp_rate)
        self.qtgui_sink_x_0_0_0.set_frequency_range(self.LO_freq, self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.iio_pluto_source_0_0.set_gain(0, self.gain)

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self._LO_freq_callback(self.LO_freq)
        self.ieee802_11_frame_equalizer_0.set_frequency(self.LO_freq)
        self.iio_pluto_source_0_0.set_frequency(self.LO_freq)
        self.qtgui_sink_x_0.set_frequency_range(self.LO_freq, self.samp_rate)
        self.qtgui_sink_x_0_0.set_frequency_range(self.LO_freq, self.samp_rate)
        self.qtgui_sink_x_0_0_0.set_frequency_range(self.LO_freq, self.samp_rate)




def main(top_block_cls=project_802_11a, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
