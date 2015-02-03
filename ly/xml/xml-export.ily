\version "2.18.2"
%{

This module defines a music function that dumps a music expression to XML


Usage e.g.:

 \displayLilyXML { c d e f }

The XML closely follows the LilyPond music structure.

All (make-music 'MusicName ...) objects translate to a <music type="MusicName">
tag. The music in the 'element and 'elements properties is put in the <element>
and <elements> tags. (LilyPond uses 'element when there is a single music
argument, and 'elements for a list of music arguments, but for example \repeat
uses both: 'element for the repeated music and 'elements for the \alternatives.

Thus <element>, if there, always has one <music> child. <elements>, if there,
can have more than one <music> child.

Each <music> element has an <origin> child element describing the source
location.




Example:

This LilyPond music:

  \relative {
    c d e
  }

maps to Scheme (using \displayMusic):

  (make-music
    'RelativeOctaveMusic
    'element
    (make-music
      'SequentialMusic
      'elements
      (list (make-music
              'NoteEvent
              'pitch
              (ly:make-pitch -1 0 0)
              'duration
              (ly:make-duration 2 0 1))
            (make-music
              'NoteEvent
              'pitch
              (ly:make-pitch -1 1 0)
              'duration
              (ly:make-duration 2 0 1))
            (make-music
              'NoteEvent
              'pitch
              (ly:make-pitch -1 2 0)
              'duration
              (ly:make-duration 2 0 1)))))

and maps to XML (using \displayLilyXML):

  <music name="RelativeOctaveMusic">
    <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="244" char="17"/>
    <element>
      <music name="SequentialMusic">
        <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="244" char="27"/>
        <elements>
          <music name="NoteEvent">
            <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="245" char="4"/>
            <pitch octave="-1" notename="0" alteration="0"/>
            <duration log="2" dots="0" numer="1" denom="1"/>
          </music>
          <music name="NoteEvent">
            <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="245" char="6"/>
            <pitch octave="-1" notename="1" alteration="0"/>
            <duration log="2" dots="0" numer="1" denom="1"/>
          </music>
          <music name="NoteEvent">
            <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="245" char="8"/>
            <pitch octave="-1" notename="2" alteration="0"/>
            <duration log="2" dots="0" numer="1" denom="1"/>
          </music>
        </elements>
      </music>
    </element>
  </music>


%}

% convert an assoc list to an xml attribute string (joined with a space in between)
#(define (attrs->string attrs)
   (string-join
     (map (lambda (e)
            (attr->string (car e) (cdr e))) attrs)
     " " 'prefix))
  
% convert a name value pair to an xml attribute
% name is a symbol, value can be a symbol, string, or number
#(define (attr->string name value)
   (string-append (symbol->string name)
     "=\""
     (cond 
      ((string? value) (attribute-escape value))
      ((number? value) (number->string value))
      ((symbol? value) (symbol->string value)))
     "\""))

% escape string for xml body
#(define (xml-escape s)
   (ly:string-substitute "<" "&lt;" 
     (ly:string-substitute ">" "&gt;" 
       (attribute-escape s))))

% escape string for xml attribute
#(define (attribute-escape s)
   (ly:string-substitute "\"" "&quot;"
     (ly:string-substitute "&" "&amp;" s)))


% output an XML tag
% indent: number of spaces
% tag-name: symbol
% attrs: assoc list
% how can be:
%   'open-tag:		write an open-tag with attributes <element bla="blabla">
%   'close-tag:		write a close-tag (attrs are ignored) </element>
%   'open-close-tag:   write a self-closing tag <element bla="blabla"/>
% port: the output port (#f selects the current output port)
#(define (output-xml-tag indent tag-name attrs how port)
   (let ((s (string-append
             (make-string (* indent) #\space)
             "<"
             (if (eq? how 'close-tag) "/" "")
             (symbol->string tag-name)
             (if (eq? how 'close-tag) "" (attrs->string attrs))
             (if (eq? how 'open-close-tag) "/" "")
             ">\n"))
         (port (if (port? port) port (current-output-port))))
     (display s port)))
  

% a nice class that outputs an XML document
% (define x (XML))
% (x 'open-tag 'name attrs)
% (x 'open-close-tag 'name attrs)
% (x 'close-tag)
% when an open tag is closed and it has no child tags, it is automatically
% written to output as an open-close tag.
#(define XML
  (lambda ()
    (define indent-width 2)
    (define pending #f)
    (define tags '())
    
    (define (output-last-tag how)
      (let* ((indent (* (- (length tags) 1) indent-width))
             (tag-name (caar tags))
             (attrs (cadar tags)))
        (output-xml-tag indent tag-name attrs how #f)))
    
    (define (open-tag args)
      (if pending
          (output-last-tag 'open-tag))
      (set! tags (cons args tags))
      (set! pending #t))
    
    (define (close-tag)
      (if pending
          (output-last-tag 'open-close-tag)
          (output-last-tag 'close-tag))
      (set! pending #f)
      (set! tags (cdr tags)))

    (lambda (method-name . args)
      (case method-name
        ((open-tag) (open-tag args))
        ((close-tag) (close-tag))
        ((open-close-tag) (open-tag args) (close-tag))))))


% convert a markup object to XML
#(define (markup->lily-xml o xml)
   (xml 'open-tag 'markup '())
   (xml 'close-tag))


% convert any object to XML
% currently the xml is just (display)ed but later it will be written to a file or string.
% the object is always returned
% xml is an XML instance
#(define (obj->lily-xml o xml)
   (cond
    ((ly:music? o)
      (let ((name (ly:music-property o 'name))
            (e (ly:music-property o 'element))
            (es (ly:music-property o 'elements))
            (as (ly:music-property o 'articulations))
            (tw (ly:music-property o 'tweaks))
            (location (ly:music-property o 'origin))
            (pitch (ly:music-property o 'pitch))
            (duration (ly:music-property o 'duration))
            (properties
             (filter
              (lambda (prop)
                (not (memq (car prop)
                       '(name element elements articulations tweaks origin pitch duration))))
              (ly:music-mutable-properties o)))
            )
        (xml 'open-tag 'music (acons 'name name '()))
        (if (ly:input-location? location)
            (let ((origin (ly:input-file-line-char-column location)))
              (xml 'open-close-tag 'origin
                `((filename . ,(car origin))
                  (line     . ,(cadr origin))
                  (char     . ,(caddr origin))))))
        (if (ly:pitch? pitch)
            (xml 'open-close-tag 'pitch
              `((octave . ,(ly:pitch-octave pitch))
                (notename . ,(ly:pitch-notename pitch))
                (alteration . ,(ly:pitch-alteration pitch)))))
        (if (ly:duration? duration)
            (xml 'open-close-tag 'duration
              `((log . ,(ly:duration-log duration))
                   (dots . ,(ly:duration-dot-count duration))
                   (numer . ,(car (ly:duration-factor duration)))
                   (denom . ,(cdr (ly:duration-factor duration))))))
        (if (ly:music? e)
            (begin 
              (xml 'open-tag 'element '())
              (obj->lily-xml e xml)
              (xml 'close-tag)))
        (if (and (list? es) (not (null? es)))
            (begin 
              (xml 'open-tag 'elements '())
              (for-each (lambda (e)
                          (obj->lily-xml e xml)) es)
              (xml 'close-tag 'elements)))
        (if (and (list? as) (not (null? as)))
            (begin 
              (xml 'open-tag 'articulations '())
              (for-each (lambda (e)
                          (obj->lily-xml e xml)) as)
              (xml 'close-tag 'articulations )))
        (if (and (list? tw) (not (null? tw)))
            (begin 
              (xml 'open-tag 'tweaks '())
              (for-each (lambda (e)
                          (obj->lily-xml e xml)) tw)
              (xml 'close-tag 'tweaks)))
        (for-each (lambda (prop)
                    (xml 'open-tag 'property `((name . ,(car prop))))
                    (obj->lily-xml (cdr prop) xml)
                    (xml 'close-tag)) properties)
        (xml 'close-tag)))
    
    ((and (markup? o) (not (string? o)))
     (markup->lily-xml o xml))
    ((number? o)
     (xml 'open-close-tag 'number `((value . ,o))))
    ((string? o)
     (xml 'open-close-tag 'string `((value  . ,o))))
    ((char? o)
     (xml 'open-close-tag 'char `((value . ,(string o)))))
    ((boolean? o)
     (xml 'open-close-tag 'boolean `((value . ,(if o 'true 'false)))))
    ((symbol? o)
     (xml 'open-close-tag 'symbol `((value . ,o))))
    ((null? o)
     (xml 'open-close-tag 'null '())) ; or <list/> ??
    ((list? o)
     (begin
       (xml 'open-tag 'list '())
       (for-each (lambda (e)
                   (obj->lily-xml e xml)) o)
       (xml 'close-tag)))
    ((pair? o)
     (begin
       (xml 'open-tag 'pair '())
       (obj->lily-xml (car o) xml)
       (obj->lily-xml (cdr o) xml)
       (xml 'close-tag)))
    ((procedure? o)
     (xml 'open-close-tag 'procedure `((name . ,(procedure-name o)))))
    ((ly:stencil? o)
     (xml 'open-close-tag 'stencil '()))
      
    )
  
  
  o)


displayLilyXML = #
(define-music-function (parser location music) (ly:music?)
  (let ((xml (XML)))
    (obj->lily-xml music xml)))

