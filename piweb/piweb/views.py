from django.views.generic import TemplateView
from django.shortcuts import render
from piweb.models import TempReading, TempSeries
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import seaborn as sbn
import StringIO
import psutil
import datetime as dt
from dateutil.relativedelta import relativedelta
from debug_toolbar_line_profiler import profile_additional

class HomeView(TemplateView):
    template_name = 'piweb/home.html'
    
    def get_context_data(self, **kwargs):
        today = dt.date.today()
        ayearago = today - relativedelta(years=1)
        
        upstairs = TempSeries.objects.get(name='Upstairs')
        upstairstemps = upstairs.tempreading_set.filter(timestamp__gte=ayearago)
        upstairstemps = upstairstemps.order_by('timestamp')
        
        df = pd.DataFrame(list(upstairstemps.values()))

        context = super(HomeView, self).get_context_data(**kwargs)
        context['today'] = today
        context['ayearago'] = ayearago
        context['htmltable'] = df.tail(10).to_html()
        
        return context

class TestView(TemplateView):
    template_name = 'piweb/test.html'
    
    def get_context_data(self, **kwargs):
        lim = self.request.GET.get('limit', 3000)

        upstairs = TempSeries.objects.get(name='Upstairs')
        upstairstemps = upstairs.tempreading_set.all().order_by('-timestamp')[:lim]

        frame = pd.DataFrame(list(upstairstemps.values()))
        frame.set_index('timestamp', inplace=True)
        
        # matplotlib.rcParams['svg.fonttype'] = 'none'

        fig = Figure()
        ax = fig.add_subplot(1,1,1)
        frame['value'].plot(ax=ax)
        ax.get_xaxis().grid(color='w', linewidth=1)
    	ax.get_yaxis().grid(color='w', linewidth=1)

        fig.set(facecolor='w')
        canvas = FigureCanvas(fig)
        
        imgdata = StringIO.StringIO()
        canvas.print_svg(imgdata)
        
        imgstr = imgdata.getvalue()
        
        context = super(TestView, self).get_context_data(**kwargs)
        context['svgtext'] = imgstr
        context['htmltable'] = frame[:12].to_html()
        context['mempct'] = psutil.virtual_memory().percent

        return context

def testview2(request):
    df = pd.DataFrame({'a': np.random.randn(10), 'b': np.random.randn(10)})
    htmltable = df.to_html()
    context = {}
    context['htmltable'] = htmltable

    return render(request, 'piweb/test2.html', context)

@profile_additional(TestView.get_context_data)
def testview3(request):
    return TestView.as_view()(request)
