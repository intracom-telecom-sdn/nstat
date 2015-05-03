#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <float.h>
#include <getopt.h>
#include <math.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <stdbool.h>
#include <pthread.h>
#include <netinet/tcp.h>
#include <stdarg.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <sys/time.h>

#include <openflow/openflow.h>

#include "myargs.h"
#include "cbench.h"
#include "fakeswitch.h"

#ifdef USE_EPOLL
#include <sys/epoll.h>
#define MAX_EVENTS  16
#endif


#define PROG_TITLE "USAGE: cbench [option]  # by Rob Sherwood 2010"

struct myargs my_options[] = {
    {"controller",  'c', "hostname of controller to connect to", MYARGS_STRING, {.string = "localhost"}},
    {"debug",       'd', "enable debugging", MYARGS_FLAG, {.flag = 0}},
    {"debug-threads",   'q', "enable thread level debugging (only thread level messages and not switch messages)", MYARGS_FLAG, {.flag= 0}},
    {"help",        'h', "print this message", MYARGS_NONE, {.none = 0}},
    {"loops",       'l', "loops per test",   MYARGS_INTEGER, {.integer = 16}},
    {"mac-addresses", 'M', "unique source MAC addresses per switch", MYARGS_INTEGER, {.integer = 100000}},
    {"ms-per-test", 'm', "test length in ms", MYARGS_INTEGER, {.integer = 1000}},
    {"port",        'p', "controller port",  MYARGS_INTEGER, {.integer = OFP_TCP_PORT}},
    {"throughput",  't', "test throughput instead of latency", MYARGS_NONE, {.none = 0}},
    {"warmup",  'w', "loops to be disregarded on test start (warmup)", MYARGS_INTEGER, {.integer = 1}},
    {"cooldown",  'C', "loops to be disregarded at test end (cooldown)", MYARGS_INTEGER, {.integer = 0}},
    {"delay",  'D', "delay starting testing after features_reply is received (in ms)", MYARGS_INTEGER, {.integer = 0}},
    {"switch-add-delay",  'e', "delay between switch addition (in nanosec)", MYARGS_INTEGER, {.integer = 0}},
    {"switches-per-thread",  'S', "switches per thread", MYARGS_INTEGER, {.integer = 1}},
    {"delay-per-thread",  'T', "delay per thread", MYARGS_INTEGER, {.integer = 1}}, 
    {"total-threads",  'Z', "total cbench threads", MYARGS_INTEGER, {.integer = 1}}, 
    {"learn-dst-macs",  'L', "send gratuitious ARP replies to learn destination macs before testing", MYARGS_FLAG, {.flag = 1}},
    {0, 0, 0, 0}
};


void debug_thread_msg(struct cbench_thr_args * args, char * msg, ...)
{
    va_list aq;

    if(args->debug_threads == 0 )
        return;

    if (args->tid == -1) {

        fprintf(stderr,"\n-------Master Thread: ");
         va_start(aq,msg);
         vfprintf(stderr,msg,aq);
        if(msg[strlen(msg)-1] != '\n')
            fprintf(stderr, "\n");
    }

    else {

    fprintf(stderr,"\n-------Thread %d: ", args->tid);
    va_start(aq,msg);
    vfprintf(stderr,msg,aq);
    if(msg[strlen(msg)-1] != '\n')
        fprintf(stderr, "\n");
    }

    return;
}

struct cbench_thr_args initialize_thread_struct (int argc, char * argv[]) {
    
    struct cbench_thr_args my_thread_args;

    my_thread_args.controller_hostname = myargs_get_default_string(my_options,"controller");
    my_thread_args.controller_port      = myargs_get_default_integer(my_options, "port");
    my_thread_args.total_mac_addresses = myargs_get_default_integer(my_options, "mac-addresses");
    my_thread_args.mstestlen = myargs_get_default_integer(my_options, "ms-per-test");
    my_thread_args.tests_per_loop = myargs_get_default_integer(my_options, "loops");
    my_thread_args.debug = myargs_get_default_flag(my_options, "debug");
    my_thread_args.warmup = myargs_get_default_integer(my_options, "warmup");
    my_thread_args.cooldown = myargs_get_default_integer(my_options, "cooldown");
    my_thread_args.delay = myargs_get_default_integer(my_options, "delay");
    my_thread_args.switch_add_delay = myargs_get_default_integer(my_options, "switch-add-delay");
    my_thread_args.learn_dst_macs = myargs_get_default_flag(my_options, "learn-dst-macs");
    my_thread_args.mode = MODE_LATENCY;
    my_thread_args.delay_per_thread = myargs_get_default_integer(my_options, "delay-per-thread");
    my_thread_args.n_fakeswitches = myargs_get_default_integer(my_options, "switches-per-thread");
    my_thread_args.total_threads = myargs_get_default_integer(my_options, "total-threads");
    my_thread_args.debug_threads = myargs_get_default_flag(my_options, "debug-threads");
    const struct option * long_opts = myargs_to_long(my_options);
    char * short_opts = myargs_to_short(my_options);
    my_thread_args.delay_is_over = false;

    /* parse args here */
    while(1)
    {
        int c;
        int option_index=0;
        c = getopt_long(argc, argv, short_opts, long_opts, &option_index);
        if (c == -1)
            break;
        switch (c) {
            case 'q' :
                my_thread_args.debug_threads = 1;
                break;
            case 'Z' :
                my_thread_args.total_threads = atoi(optarg);
                break;   
            case 'S' :
                my_thread_args.n_fakeswitches = atoi(optarg);
                break;
            case 'T' :
                my_thread_args.delay_per_thread = atoi(optarg);
                break;
            case 'c' :  
                my_thread_args.controller_hostname = strdup(optarg);
                break;
            case 'd':
                my_thread_args.debug = 1;
                break;
            case 'h': 
                myargs_usage(my_options, PROG_TITLE, "help message", NULL, 1);
                break;
            case 'L':
                if(optarg)
                    my_thread_args.learn_dst_macs = ( strcasecmp("true", optarg) == 0 || strcasecmp("on", optarg) == 0 || strcasecmp("1", optarg) == 0);
                else
                    my_thread_args.learn_dst_macs = 1;
                break;
            case 'l': 
                my_thread_args.tests_per_loop = atoi(optarg);
                break;
            case 'M':
                my_thread_args.total_mac_addresses = atoi(optarg);
                break;
            case 'm': 
                my_thread_args.mstestlen = atoi(optarg);
                break;
            case 'p' : 
                my_thread_args.controller_port = atoi(optarg);
                break;;
            case 't': 
                my_thread_args.mode = MODE_THROUGHPUT;
                break;
            case 'w': 
                my_thread_args.warmup = atoi(optarg);
                break;
            case 'C': 
                my_thread_args.cooldown = atoi(optarg);
                break;
            case 'D':
                my_thread_args.delay = atoi(optarg);
                break;
            case 'e':
                my_thread_args.switch_add_delay = atoi(optarg);
                break;
            default: 
                myargs_usage(my_options, PROG_TITLE, "help message", NULL, 1);
        }
    }

    return my_thread_args;
}



/*******************************************************************/
double run_test(struct cbench_thr_args *args, struct fakeswitch * fakeswitches)
{
    struct timeval now, then, diff;
    struct  pollfd  * pollfds;
    int i;
    double sum = 0;
    double passed;
    int count;
    bool started_test = false;
    int initialized_switches = 0;
    int total_wait = args->mstestlen + args->delay;
    time_t tNow;
    struct tm *tmNow;

    pollfds = malloc(args->n_fakeswitches * sizeof(struct pollfd));
    assert(pollfds);
    
    while(1)
    {
        if ( (*(args->threads_started) == args->total_threads) && (!started_test) ) {
            started_test = true;
            gettimeofday(&then,NULL);
            debug_thread_msg(args,"Started at msec: %02d. Should be almost equal with other threads for efficient synchronization\n", then.tv_usec);
        }

        if ( *(args->threads_started) == args->total_threads ) {
            gettimeofday(&now, NULL);
            timersub(&now, &then, &diff);
            if( (1000* diff.tv_sec  + (float)diff.tv_usec/1000) > total_wait)
                break;
            else if ((1000* diff.tv_sec  + (float)diff.tv_usec/1000) > args->delay)
                args->delay_is_over = true;
        }

        #ifdef USE_EPOLL
        for(i = 0; i < MAX_EVENTS; i++) {
            (args->events[i]).events = EPOLLIN | EPOLLOUT;
        }
        
        int nfds = epoll_wait(args->epollfd, args->events, MAX_EVENTS, -1);

        for(i = 0; i < nfds; i++) {
            fakeswitch_handle_io(args->events[i].data.ptr, &(args->events[i].events), &initialized_switches, args);
        }
        #else
        for(i = 0; i < args->n_fakeswitches; i++) 
            fakeswitch_set_pollfd(&fakeswitches[i], &pollfds[i]);
        
        poll(pollfds, args->n_fakeswitches, 1000);

        for(i = 0; i < args->n_fakeswitches; i++) 
            fakeswitch_handle_io(&fakeswitches[i], &pollfds[i], &initialized_switches, args);
        #endif
    }

   usleep(100000); // sleep for 100 ms, to let packets queue
  
   for( i = 0 ; i < args->n_fakeswitches; i++)
   {
       count = fakeswitch_get_count(&fakeswitches[i]);
       args->global_results[(args->tid)*(args->n_fakeswitches) + i] = count;
   }
    
   free(pollfds);
   return sum;
}

/********************************************************************************/

int timeout_connect(int fd, const char * hostname, int port, int mstimeout) {
    int ret = 0;
    int flags;
    fd_set fds;
    struct timeval tv;
    struct addrinfo *res=NULL;
    struct addrinfo hints;
    char sport[BUFLEN];
    int err;

    hints.ai_flags          = 0;
    hints.ai_family         = AF_INET;
    hints.ai_socktype       = SOCK_STREAM;
    hints.ai_protocol       = IPPROTO_TCP;
    hints.ai_addrlen        = 0;
    hints.ai_addr           = NULL;
    hints.ai_canonname      = NULL;
    hints.ai_next           = NULL;

    snprintf(sport,BUFLEN,"%d",port);

    err = getaddrinfo(hostname,sport,&hints,&res);
    if(err|| (res==NULL))
    {
        if(res)
            freeaddrinfo(res);
        return -1;
    }

    // set non blocking
    if((flags = fcntl(fd, F_GETFL)) < 0) {
        fprintf(stderr, "timeout_connect: unable to get socket flags\n");
        freeaddrinfo(res);
        return -1;
    }
    if(fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        fprintf(stderr, "timeout_connect: unable to put the socket in non-blocking mode\n");
        freeaddrinfo(res);
        return -1;
    }
    
    #ifdef USE_EPOLL
    struct epoll_event ev;
    int epollfd = epoll_create(1);
    ev.events = EPOLLIN | EPOLLOUT | EPOLLERR;
    ev.data.fd = fd;
    if(epoll_ctl(epollfd, EPOLL_CTL_ADD, fd, &ev) == -1) {
        printf("Cannot use epoll to create connection\n");
        return -1;
    }
    #else
    FD_ZERO(&fds);
    FD_SET(fd, &fds);
    #endif

    if(mstimeout >= 0) 
    {
        tv.tv_sec = mstimeout / 1000;
        tv.tv_usec = (mstimeout % 1000) * 1000;

        errno = 0;

        if(connect(fd, res->ai_addr, res->ai_addrlen) < 0) 
        {
            if((errno != EWOULDBLOCK) && (errno != EINPROGRESS))
            {
                fprintf(stderr, "timeout_connect: error connecting: %d\n", errno);
                freeaddrinfo(res);
                return -1;
            }
        }
        #ifdef USE_EPOLL
        int nfds = epoll_wait(epollfd, &ev, 1, mstimeout);
        #else
        ret = select(fd + 1, NULL, &fds, NULL, &tv);
        #endif
    }
    freeaddrinfo(res);

    #ifdef USE_EPOLL
    close(epollfd);
    
    if(ev.events & EPOLLERR) {
        return -1;
    } else {
        return 0;
    }
    #else
    if(ret != 1) 
    {
            if(ret == 0)
                return -1;
            else
                return ret;
    }
    return 0;
    #endif
}

/********************************************************************************/
int make_tcp_connection_from_port(const char * hostname, unsigned short port, unsigned short sport,
        int mstimeout, int nodelay)
{
    struct sockaddr_in local;
    int s;
    int err;
    int zero = 0;

    s = socket(AF_INET,SOCK_STREAM,0);
    if(s<0){
        perror("make_tcp_connection: socket");
        exit(1);  // bad socket
    }
    if(nodelay && (setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &zero, sizeof(zero)) < 0))
    {
        perror("setsockopt");
        fprintf(stderr,"make_tcp_connection::Unable to disable Nagle's algorithm\n");
        exit(1);
    }
    local.sin_family=PF_INET;
    local.sin_addr.s_addr=INADDR_ANY;
    local.sin_port=htons(sport);

    err=bind(s,(struct sockaddr *)&local, sizeof(local));
    if(err)
    {
        perror("make_tcp_connection_from_port::bind");
        return -4;
    }

    err = timeout_connect(s,hostname,port, mstimeout);

    if(err)
    {
        perror("make_tcp_connection: connect");
        close(s);
        return err; // bad connect
    }
    return s;
}

/********************************************************************************/
int make_tcp_connection(const char * hostname, unsigned short port, int mstimeout, int nodelay)
{
    return make_tcp_connection_from_port(hostname,port, INADDR_ANY, mstimeout, nodelay);
}

/********************************************************************************/
int count_bits(int n)
{
    int count =0;
    int i;
    for(i=0; i< 32;i++)
        if( n & (1<<i))
            count ++;
    return count;
}


void print_thread_arguments ( struct cbench_thr_args* args)
{

    fprintf(stderr, "\n Controller=%s \n Port=%d \n Fake Switches = %d \n Dpid Offset = %d \n"
                    "Delay Per Thread = %d \n Tests Per Loop = %d \n Debug = %d \n "
                    "Mac addresses = %d \n Learn Dst Macs = %d \n MSTest = %d \n Warmup = %d "
                    "Cooldown = %d \n Switch add delay = %d \n",
                    args->controller_hostname, 
                    args->controller_port,
                    args->n_fakeswitches,
                    args->dpid_offset, 
                    args->delay_per_thread, 
                    args->tests_per_loop,
                    args->debug, 
                    args->total_mac_addresses, 
                    args->learn_dst_macs, 
                    args->mstestlen, 
                    args->warmup , 
                    args->cooldown, 
                    args->switch_add_delay);

    return;
}

/********************************************************************************/

/* 
     Function that each thread will execute. It represents a cbench instance 
     emulating different switches. All cbench-threads will initialize their switches
     and answer to statistics and messages from the controller but WILL NOT initiate
     traffic UNTIL all threads have initialized all their switches. This is achieved 
     by accessing a pointer to a common thread variable. Each thread increments atomically
     this variable when it sends the last FEATURES_REQUEST reply. When this variable is 
     equal to the total number of threads, traffic will be initiated by all threads. 
     In this way, full cbench topology will be up and running before any traffic is initiated.

     Synchronization between cbench-instances:
      - Barrier between loops of each run.
      - Shared variable indicating if all the threads have emulated their topology.
*/
void* cbench_thread(void *targs)
{
    struct cbench_thr_args *args = (struct cbench_thr_args*)targs;
    struct  fakeswitch *fakeswitches;
    int i,j,k;
    int epollfd;
    struct timeval now, then, diff;
    struct tm *tmNow;
    time_t tNow;
    double flows_sum, passed;

    ///print_thread_arguments(args);
    fakeswitches = (struct fakeswitch*) malloc(args->n_fakeswitches * sizeof(struct fakeswitch));
    assert(fakeswitches);
    
    double sum = 0;
    double *results;
    double  min = DBL_MAX;
    double  max = 0.0;
    double  v;
    results = malloc((args->tests_per_loop + 1)* sizeof(double));

    #ifdef USE_EPOLL
    struct epoll_event ev;
    epollfd = epoll_create(4096);
    if(epollfd == -1) {
        fprintf(stderr, "Cannot create epollfd.\n");
        exit(1);
    }
    #endif

    args->epollfd = epollfd;

    for( i = 0; i < args->n_fakeswitches; i++)
    {
        int sock;

        sock = make_tcp_connection(args->controller_hostname, args->controller_port,3000, args->mode != MODE_THROUGHPUT );
        if(sock < 0 )
        {
            fprintf(stderr, "make_nonblock_tcp_connection :: returned %d", sock);
            exit(1);
        }
        if(args->debug)
            fprintf(stderr,"Initializing switch %d ... ", i+1);
        fflush(stderr);
    usleep(args->switch_add_delay);
        #ifdef USE_EPOLL
        fakeswitch_init(&fakeswitches[i],args->dpid_offset+i,sock,BUFLEN, args->debug, args->mode, args->total_mac_addresses, args->learn_dst_macs);
        #else
        fakeswitch_init(&fakeswitches[i], 0, args->sock, 65536, args->debug, args->mode, args->total_mac_addresses, args->learn_dst_macs);
        #endif

        if(args->debug)
            fprintf(stderr," :: done.\n");
        fflush(stderr);
    
        #ifdef USE_EPOLL
        ev.events = EPOLLIN | EPOLLOUT;
        ev.data.fd = sock;
        ev.data.ptr = &fakeswitches[i];

        if(epoll_ctl(epollfd, EPOLL_CTL_ADD, sock, &ev) == -1) {
            fprintf(stderr, "Cannot add sock to epoll\n");
            exit(1);
        }
        #endif

    }    

    /*
     * Main loop that ALL threads will run. Barriers before each run for thread
     * synchronization. Thread with id = 0 will report results for flows PER loop
     * as well as the final results of the experiment.
     */
    for( j = 0; j < args->tests_per_loop; j++) {

        if (args->tid == 0) {
            debug_thread_msg(args,"Ready to run test for loop=%d\n",j);
            gettimeofday(&then, NULL);
        }   
    
        if (j > 0)
            pthread_barrier_wait(args->pointer_to_global_barrier);

        if ( j > 0 ) {
            args->delay = 0;      // only delay on the first run
            args->delay_is_over = true; 
        }
        v = 1000.0 * run_test(args, fakeswitches);

        pthread_barrier_wait(args->pointer_to_global_barrier);
            
        /* Thread-0 will calculate results and print accordingly */
        if ((args->tid == 0)) {
            gettimeofday(&now, NULL);
            timersub(&now, &then, &diff);

            tNow = now.tv_sec;
            tmNow = localtime(&tNow);
            fprintf(stderr, "%02d:%02d:%02d.%03d %-3d switches: flows:  ", 
                            tmNow->tm_hour, 
                            tmNow->tm_min, 
                            tmNow->tm_sec, 
                            (int)(now.tv_usec/1000), 
                            args->n_fakeswitches*args->total_threads);
              
            flows_sum = 0;
            for (i=0; i< (args->n_fakeswitches) * (args->total_threads); i++) {
                fprintf(stderr,"%d ",args->global_results[i]); 
                flows_sum += args->global_results[i];
            }
                   
            passed = 1000 * diff.tv_sec + (double)diff.tv_usec/1000;
            passed -= args->delay;
               
            /* For first loop ONLY assume that time passed is the mstestlen (-m). */
            if (j == 0)
                flows_sum /= args->mstestlen;
            else
                flows_sum /= passed;
               
            fprintf(stderr," total = %lf per ms \n", flows_sum);
              
            if( j < (args->warmup) || j >= (args->tests_per_loop - args->cooldown)) 
                continue;

            results[j] = flows_sum*1000;
            sum+= flows_sum*1000;
            if (flows_sum*1000 > max)
                max = flows_sum*1000;
            if (flows_sum*1000 < min)
                min = flows_sum*1000;
        }       
    }

    pthread_barrier_wait(args->pointer_to_global_barrier);
    
    if (args->tid == 0) {
        int counted_tests = (args->tests_per_loop - args->warmup - args->cooldown );
        // compute std dev
        double avg = sum / counted_tests;
        sum = 0.0;
        for (j = args->warmup; j <= args->tests_per_loop-args->cooldown; ++j) {
            sum += pow(results[j] - avg, 2);
        }
        sum = sum / (double)(counted_tests);
        double std_dev = sqrt(sum);
        fprintf(stderr,"RESULT: %d switches %d tests "
        "min/max/avg/stdev = %.2lf/%.2lf/%.2lf/%.2lf responses/s\n",
        args->n_fakeswitches * args->total_threads,counted_tests, min, max, avg, std_dev);
    }

    return (void*)0;
}


int main(int argc, char * argv[])
{
    int *global_results;
    pthread_t *tids;
    pthread_barrier_t global_barrier;
    cbench_thr_args_t *thread_arguments;
    int i, nthreads, delay,switches_per_thread; 
    
    /* 
     * In order to take all arguments provided by command line 
     * we create a temp variable with initialize_thread_struct
     */ 
    cbench_thr_args_t temp = initialize_thread_struct(argc,argv);
    
    fprintf(stderr, "cbench: controller benchmarking tool\n"
                "   running in mode %s\n"
                "   connecting to controller at %s:%d \n"
                "   faking %d switches with %d threads :: %d tests each; %d ms per test\n"
                "   with %d unique source MACs per switch\n"
                "   %s destination mac addresses before the test\n"
                "   starting test with %d ms delay after features_reply\n"
                "   ignoring first %d \"warmup\" and last %d \"cooldown\" loops\n"
                "   debugging info is %s\n",
                temp.mode == MODE_THROUGHPUT? "'throughput'": "'latency'",
                temp.controller_hostname,
                temp.controller_port,
                (temp.n_fakeswitches)*(temp.total_threads),
        temp.total_threads,
                temp.tests_per_loop,
                temp.mstestlen,
                temp.total_mac_addresses,
                temp.learn_dst_macs ? "learning" : "NOT learning",
                temp.delay,
                temp.warmup,temp.cooldown,
                temp.debug == 1 ? "on" : "off");

    
    /* Shared variable by all thread instances that indicates
     * how many threads have started their switches (sent up to 
     * FEATURES_REPLY message)
    */
    volatile int threads_started = 0;
    
    nthreads = temp.total_threads;
    delay = temp.delay_per_thread;
    switches_per_thread = temp.n_fakeswitches;
    temp.tid = -1;
    pthread_barrier_init(&global_barrier, NULL, nthreads);
   
    /* This memory will hold result for all switches per 
     * loop of the cbench function 
     */
    global_results = (int *) malloc(nthreads * switches_per_thread * sizeof(int));
    
    /* Array of cbench_thr_args_t and array of thread ids */
    thread_arguments =(cbench_thr_args_t*) malloc( nthreads * sizeof(cbench_thr_args_t));
    tids = (pthread_t*)malloc( nthreads * sizeof(pthread_t) );
    
    /* Spawn `nthreads` cbench instances. Each thread will
     * emulate a number of switches with different dpid_offsets.
     * Master thread will sleep for a fixed time between thread creation
     * in order to give the controller the chance to properly response 
     * to the initiated switches.      
    */
    for ( i = 0; i < nthreads; i++ ) {
        thread_arguments[i] = temp;
        thread_arguments[i].pointer_to_global_barrier = &global_barrier;
        thread_arguments[i].tid = i;
        thread_arguments[i].dpid_offset = i*switches_per_thread;    
        thread_arguments[i].threads_started = &threads_started;
        thread_arguments[i].global_results = global_results;
        fprintf(stderr,"Master Thread: Creating thread-%d! \n",i);
        pthread_create(&tids[i], NULL, cbench_thread, (void*)&thread_arguments[i]);
        usleep(delay*1000);
    }
 
    /* Wait for all threads to finish their execution. */ 
    for ( i = 0; i < nthreads; i++ ) {
        pthread_join(tids[i], NULL);
    }
   
    return 0;
}
