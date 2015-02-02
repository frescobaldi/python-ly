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

#(define indent-width 2)

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


% show a tag
#(define (xml-tag name indent attrs close-tag)
   (let ((s (string-append
             (make-string (* indent-width indent) #\space)
             "<"
             (if (eq? close-tag 'close) "/" "")
             (symbol->string name)
             (attrs->string attrs)
             (if (eq? close-tag 'self-close) "/" "")
             ">\n")))
     (display s)))
   
% show an open tag
#(define (open-tag name indent attrs)
   (xml-tag name indent attrs #f))

% show a close tag
#(define (close-tag name indent)
   (xml-tag name indent '() 'close))

% show a self-closing tag
#(define (self-close-tag name indent attrs)
   (xml-tag name indent attrs 'self-close))



% convert any object to XML
% currently the xml is just (display)ed but later it will be written to a file or string.
% the object is always returned
#(define (obj->lily-xml o indent)
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
            )
        (open-tag 'music indent (acons 'name name '()))
        (if (ly:input-location? location)
            (let ((origin (ly:input-file-line-char-column location)))
              (self-close-tag 'origin (+ indent 1)
                `((filename . ,(car origin))
                  (line     . ,(cadr origin))
                  (char     . ,(caddr origin))))))
        (if (ly:pitch? pitch)
            (self-close-tag 'pitch (+ indent 1)
              `((octave . ,(ly:pitch-octave pitch))
                (notename . ,(ly:pitch-notename pitch))
                (alteration . ,(ly:pitch-alteration pitch)))))
        (if (ly:duration? duration)
            (self-close-tag 'duration (+ indent 1)
              `((log . ,(ly:duration-log duration))
                   (dots . ,(ly:duration-dot-count duration))
                   (numer . ,(car (ly:duration-factor duration)))
                   (denom . ,(cdr (ly:duration-factor duration))))))
        (if (ly:music? e)
            (begin 
              (open-tag 'element (+ indent 1) '())
              (obj->lily-xml e (+ indent 2))
              (close-tag 'element (+ indent 1))))
        (if (and (list? es) (not (null? es)))
            (begin 
              (open-tag 'elements (+ indent 1) '())
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) es)
              (close-tag 'elements (+ indent 1))))
        (if (and (list? as) (not (null? as)))
            (begin 
              (open-tag 'articulations (+ indent 1) '())
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) as)
              (close-tag 'articulations (+ indent 1))))
        (if (and (list? tw) (not (null? tw)))
            (begin 
              (open-tag 'tweaks (+ indent 1) '())
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) tw)
              (close-tag 'tweaks (+ indent 1))))
        (close-tag 'music indent)))
    
    ((number? o)
     (self-close-tag 'number indent `((value . ,o))))
    ((string? o)
     (self-close-tag 'string indent `((value  . ,o))))
    ((char? o)
     (self-close-tag 'char indent `((value . ,(string o)))))
    ((boolean? o)
     (self-close-tag 'boolean indent `((value . ,(if o 'true 'false)))))
    ((symbol? o)
     (self-close-tag 'symbol indent `((value . ,o))))
    ((null? o)
     (self-close-tag 'null indent '())) ; or <list/> ??
    ((list? o)
     (begin
       (open-tag 'list indent '())
       (for-each (lambda (e)
                   (obj->lily-xml e (+ indent 1))) o)
       (close-tag 'list indent)))
    ((pair? o)
     (begin
       (open-tag 'pair indent '())
       (obj->lily-xml (car o) (+ indent 1))
       (obj->lily-xml (cdr o) (+ indent 1))
       (close-tag 'pair indent)))
      
    )
  
  
  o)


displayLilyXML = #
(define-music-function (parser location music) (ly:music?)
  (obj->lily-xml music 0))

